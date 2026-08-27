from datetime import UTC, datetime, timedelta

from app.models import (
    Category,
    InventoryCount,
    InventoryCountItem,
    InventoryCountStatus,
    Product,
    Vendor,
)
from conftest import ApiContext


def create_catalog(api_context: ApiContext):
    category = Category(name="Beverages")
    inactive_category = Category(name="Retired", is_active=False)
    vendor = Vendor(name="Drink Distributor")
    inactive_vendor = Vendor(name="Old Distributor", is_active=False)
    api_context.session.add_all([category, inactive_category, vendor, inactive_vendor])
    api_context.session.commit()
    return category, inactive_category, vendor, inactive_vendor


def test_product_permissions_validation_and_crud(api_context: ApiContext) -> None:
    category, inactive_category, vendor, inactive_vendor = create_catalog(api_context)
    api_context.login(api_context.employee)
    assert api_context.client.get("/api/v1/products").status_code == 200
    assert (
        api_context.client.post(
            "/api/v1/products",
            json={
                "sku": "NOPE",
                "name": "Denied",
                "category_id": str(category.id),
            },
        ).status_code
        == 403
    )

    api_context.login(api_context.manager)
    created = api_context.client.post(
        "/api/v1/products",
        json={
            "sku": " bev-001 ",
            "name": "Energy Drink",
            "description": "16 oz can",
            "unit_description": "can",
            "category_id": str(category.id),
            "preferred_vendor_id": str(vendor.id),
            "minimum_quantity": 5,
            "target_quantity": 12,
        },
    )
    assert created.status_code == 201
    assert created.json()["sku"] == "BEV-001"
    assert created.json()["latest_quantity"] is None
    assert created.json()["is_counted"] is False
    assert created.json()["is_low_stock"] is None
    assert created.json()["recommended_reorder_quantity"] is None
    product_id = created.json()["id"]

    duplicate = api_context.client.post(
        "/api/v1/products",
        json={
            "sku": "BeV-001",
            "name": "Duplicate",
            "category_id": str(category.id),
        },
    )
    assert duplicate.status_code == 409

    invalid_threshold = api_context.client.post(
        "/api/v1/products",
        json={
            "sku": "BEV-002",
            "name": "Invalid",
            "category_id": str(category.id),
            "minimum_quantity": 5,
            "target_quantity": 4,
        },
    )
    assert invalid_threshold.status_code == 422
    assert (
        api_context.client.post(
            "/api/v1/products",
            json={
                "sku": "BEV-003",
                "name": "Inactive category",
                "category_id": str(inactive_category.id),
            },
        ).status_code
        == 400
    )
    assert (
        api_context.client.patch(
            f"/api/v1/products/{product_id}",
            json={"preferred_vendor_id": str(inactive_vendor.id)},
        ).status_code
        == 400
    )

    updated = api_context.client.patch(
        f"/api/v1/products/{product_id}",
        json={"name": "Updated Energy Drink", "is_active": False},
    )
    assert updated.status_code == 200
    assert updated.json()["is_active"] is False


def test_latest_quantity_ignores_drafts_and_supports_filters(api_context: ApiContext) -> None:
    category, _inactive_category, vendor, _inactive_vendor = create_catalog(api_context)
    low = Product(
        sku="LOW-001",
        name="Low Product",
        category=category,
        preferred_vendor=vendor,
        minimum_quantity=5,
        target_quantity=12,
    )
    adequate = Product(
        sku="OK-001",
        name="Adequate Product",
        category=category,
        minimum_quantity=2,
        target_quantity=8,
    )
    uncounted = Product(
        sku="NEW-001",
        name="Uncounted Product",
        category=category,
        minimum_quantity=3,
        target_quantity=10,
    )
    submitted_at = datetime.now(UTC) - timedelta(hours=1)
    submitted = InventoryCount(
        status=InventoryCountStatus.SUBMITTED,
        started_by=api_context.employee,
        submitted_by=api_context.employee,
        submitted_at=submitted_at,
        items=[
            InventoryCountItem(product=low, quantity=3),
            InventoryCountItem(product=adequate, quantity=4),
        ],
    )
    draft = InventoryCount(
        status=InventoryCountStatus.DRAFT,
        started_by=api_context.employee,
        items=[InventoryCountItem(product=low, quantity=99)],
    )
    api_context.session.add_all([uncounted, submitted, draft])
    api_context.session.commit()
    api_context.login(api_context.employee)

    detail = api_context.client.get(f"/api/v1/products/{low.id}")
    assert detail.status_code == 200
    assert detail.json()["latest_quantity"] == 3
    assert detail.json()["is_low_stock"] is True
    assert detail.json()["recommended_reorder_quantity"] == 9

    low_listing = api_context.client.get("/api/v1/products?is_low_stock=true")
    assert [item["sku"] for item in low_listing.json()["items"]] == ["LOW-001"]
    uncounted_listing = api_context.client.get("/api/v1/products?is_counted=false")
    assert [item["sku"] for item in uncounted_listing.json()["items"]] == ["NEW-001"]
    search = api_context.client.get("/api/v1/products?search=adequate")
    assert search.json()["total"] == 1

    history = api_context.client.get(f"/api/v1/products/{low.id}/count-history")
    assert history.status_code == 200
    assert history.json()["total"] == 1
    assert history.json()["items"][0]["quantity"] == 3
