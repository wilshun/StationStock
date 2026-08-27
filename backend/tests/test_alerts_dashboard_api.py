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


def seed_dashboard_scenario(api_context: ApiContext):
    category = Category(name="Drinks")
    other_category = Category(name="Candy")
    vendor = Vendor(name="Primary Vendor")
    low_urgent = Product(
        sku="LOW-URGENT",
        name="Urgent Product",
        category=category,
        preferred_vendor=vendor,
        minimum_quantity=5,
        target_quantity=20,
    )
    low_other = Product(
        sku="LOW-OTHER",
        name="Other Low Product",
        category=other_category,
        minimum_quantity=4,
        target_quantity=10,
    )
    adequate = Product(
        sku="ADEQUATE",
        name="Adequate Product",
        category=category,
        minimum_quantity=3,
        target_quantity=8,
    )
    uncounted = Product(
        sku="UNCOUNTED",
        name="Uncounted Product",
        category=category,
        minimum_quantity=2,
        target_quantity=6,
    )
    older = InventoryCount(
        status=InventoryCountStatus.SUBMITTED,
        started_by=api_context.employee,
        submitted_by=api_context.employee,
        submitted_at=datetime.now(UTC) - timedelta(days=1),
        items=[
            InventoryCountItem(product=low_urgent, quantity=4),
            InventoryCountItem(product=low_other, quantity=1),
            InventoryCountItem(product=adequate, quantity=7),
        ],
    )
    newer = InventoryCount(
        status=InventoryCountStatus.SUBMITTED,
        started_by=api_context.manager,
        submitted_by=api_context.manager,
        submitted_at=datetime.now(UTC),
        items=[InventoryCountItem(product=low_urgent, quantity=2)],
    )
    ignored_draft = InventoryCount(
        status=InventoryCountStatus.DRAFT,
        started_by=api_context.employee,
        items=[InventoryCountItem(product=uncounted, quantity=0)],
    )
    api_context.session.add_all([older, newer, ignored_draft])
    api_context.session.commit()
    return category, other_category, vendor


def test_low_stock_alerts_exclude_uncounted_and_order_by_target_shortage(
    api_context: ApiContext,
) -> None:
    category, other_category, vendor = seed_dashboard_scenario(api_context)
    assert api_context.client.get("/api/v1/alerts/low-stock").status_code == 401
    api_context.login(api_context.employee)

    response = api_context.client.get("/api/v1/alerts/low-stock")

    assert response.status_code == 200
    assert response.json()["total"] == 2
    assert [item["sku"] for item in response.json()["items"]] == [
        "LOW-URGENT",
        "LOW-OTHER",
    ]
    assert response.json()["items"][0]["recommended_reorder_quantity"] == 18
    assert "UNCOUNTED" not in response.text

    category_filter = api_context.client.get(
        f"/api/v1/alerts/low-stock?category_id={other_category.id}"
    )
    assert category_filter.json()["total"] == 1
    vendor_filter = api_context.client.get(
        f"/api/v1/alerts/low-stock?preferred_vendor_id={vendor.id}"
    )
    assert vendor_filter.json()["total"] == 1


def test_dashboard_returns_real_aggregates_and_recent_order(api_context: ApiContext) -> None:
    seed_dashboard_scenario(api_context)
    api_context.login(api_context.manager)

    response = api_context.client.get("/api/v1/dashboard/summary")

    assert response.status_code == 200
    body = response.json()
    assert body["active_product_count"] == 4
    assert body["low_stock_product_count"] == 2
    assert body["uncounted_active_product_count"] == 1
    assert body["active_category_count"] == 2
    assert body["active_vendor_count"] == 1
    assert body["total_submitted_count_sessions"] == 2
    assert len(body["recent_submitted_count_sessions"]) == 2
    assert body["recent_submitted_count_sessions"][0]["submitted_by"]["role"] == "manager"
    assert [item["sku"] for item in body["prioritized_low_stock"]] == [
        "LOW-URGENT",
        "LOW-OTHER",
    ]
