import uuid

from app.models import Category, InventoryCount, InventoryCountStatus, Product
from conftest import ApiContext


def create_products(api_context: ApiContext) -> tuple[Product, Product]:
    category = Category(name="Snacks")
    active = Product(
        sku="SNK-001",
        name="Chips",
        category=category,
        minimum_quantity=5,
        target_quantity=12,
    )
    inactive = Product(
        sku="SNK-002",
        name="Retired Chips",
        category=category,
        is_active=False,
    )
    api_context.session.add_all([active, inactive])
    api_context.session.commit()
    return active, inactive


def test_draft_item_lifecycle_and_validation(api_context: ApiContext) -> None:
    active, inactive = create_products(api_context)
    assert api_context.client.post("/api/v1/inventory-counts", json={}).status_code == 401
    api_context.login(api_context.employee)
    created = api_context.client.post(
        "/api/v1/inventory-counts",
        json={"notes": "Evening count"},
    )
    assert created.status_code == 201
    count_id = created.json()["id"]
    assert created.json()["status"] == "draft"
    assert created.json()["started_by"]["id"] == str(api_context.employee.id)

    negative = api_context.client.put(
        f"/api/v1/inventory-counts/{count_id}/items/{active.id}",
        json={"quantity": -1},
    )
    assert negative.status_code == 422
    inactive_response = api_context.client.put(
        f"/api/v1/inventory-counts/{count_id}/items/{inactive.id}",
        json={"quantity": 2},
    )
    assert inactive_response.status_code == 400

    added = api_context.client.put(
        f"/api/v1/inventory-counts/{count_id}/items/{active.id}",
        json={"quantity": 3, "notes": "Three on shelf"},
    )
    assert added.status_code == 200
    assert len(added.json()["items"]) == 1
    assert added.json()["items"][0]["quantity"] == 3

    replaced = api_context.client.put(
        f"/api/v1/inventory-counts/{count_id}/items/{active.id}",
        json={"quantity": 4},
    )
    assert replaced.status_code == 200
    assert len(replaced.json()["items"]) == 1
    assert replaced.json()["items"][0]["quantity"] == 4

    removed = api_context.client.delete(
        f"/api/v1/inventory-counts/{count_id}/items/{active.id}"
    )
    assert removed.status_code == 204
    detail = api_context.client.get(f"/api/v1/inventory-counts/{count_id}")
    assert detail.json()["items"] == []


def test_draft_ownership_and_manager_override(api_context: ApiContext) -> None:
    active, _inactive = create_products(api_context)
    manager_draft = InventoryCount(started_by=api_context.manager)
    api_context.session.add(manager_draft)
    api_context.session.commit()

    api_context.login(api_context.employee)
    forbidden = api_context.client.patch(
        f"/api/v1/inventory-counts/{manager_draft.id}",
        json={"notes": "Not allowed"},
    )
    assert forbidden.status_code == 403

    employee_draft = api_context.client.post("/api/v1/inventory-counts", json={})
    employee_count_id = employee_draft.json()["id"]
    api_context.login(api_context.manager)
    manager_edit = api_context.client.put(
        f"/api/v1/inventory-counts/{employee_count_id}/items/{active.id}",
        json={"quantity": 6},
    )
    assert manager_edit.status_code == 200


def test_submission_is_atomic_immutable_and_updates_official_quantity(
    api_context: ApiContext,
) -> None:
    active, _inactive = create_products(api_context)
    api_context.login(api_context.employee)
    empty = api_context.client.post("/api/v1/inventory-counts", json={})
    empty_id = empty.json()["id"]
    failed_submit = api_context.client.post(
        f"/api/v1/inventory-counts/{empty_id}/submit"
    )
    assert failed_submit.status_code == 400
    api_context.session.expire_all()
    assert (
        api_context.session.get(InventoryCount, uuid.UUID(empty_id)).status
        is InventoryCountStatus.DRAFT
    )

    draft = api_context.client.post("/api/v1/inventory-counts", json={})
    count_id = draft.json()["id"]
    assert (
        api_context.client.put(
            f"/api/v1/inventory-counts/{count_id}/items/{active.id}",
            json={"quantity": 2},
        ).status_code
        == 200
    )
    before_submit = api_context.client.get(f"/api/v1/products/{active.id}")
    assert before_submit.json()["latest_quantity"] is None

    submitted = api_context.client.post(
        f"/api/v1/inventory-counts/{count_id}/submit"
    )
    assert submitted.status_code == 200
    assert submitted.json()["status"] == "submitted"
    assert submitted.json()["submitted_at"] is not None
    assert submitted.json()["submitted_by"]["id"] == str(api_context.employee.id)

    product = api_context.client.get(f"/api/v1/products/{active.id}")
    assert product.json()["latest_quantity"] == 2
    assert product.json()["is_low_stock"] is True
    assert product.json()["recommended_reorder_quantity"] == 10

    assert (
        api_context.client.patch(
            f"/api/v1/inventory-counts/{count_id}", json={"notes": "Changed"}
        ).status_code
        == 409
    )
    assert (
        api_context.client.post(
            f"/api/v1/inventory-counts/{count_id}/submit"
        ).status_code
        == 409
    )
    assert (
        api_context.client.delete(
            f"/api/v1/inventory-counts/{count_id}/items/{active.id}"
        ).status_code
        == 409
    )

    listing = api_context.client.get(
        f"/api/v1/inventory-counts?status=submitted&user_id={api_context.employee.id}"
    )
    assert listing.status_code == 200
    assert listing.json()["total"] == 1
    assert listing.json()["items"][0]["item_count"] == 1
