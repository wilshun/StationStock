from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.api.schemas.dashboard import DashboardSummary, RecentCountSummary
from app.api.schemas.inventory_counts import UserSummary
from app.auth.dependencies import CurrentUser
from app.db.session import get_db
from app.models import (
    Category,
    InventoryCount,
    InventoryCountItem,
    InventoryCountStatus,
    Product,
    Vendor,
)
from app.services.inventory import (
    latest_inventory_subquery,
    low_stock_response,
    low_stock_statement,
)


router = APIRouter(prefix="/v1/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    _current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> DashboardSummary:
    latest = latest_inventory_subquery()
    active_product_count = db.scalar(
        select(func.count()).select_from(Product).where(Product.is_active.is_(True))
    ) or 0
    low_stock_product_count = db.scalar(
        select(func.count())
        .select_from(Product)
        .join(latest, latest.c.product_id == Product.id)
        .where(
            Product.is_active.is_(True),
            latest.c.quantity < Product.minimum_quantity,
        )
    ) or 0
    uncounted_active_product_count = db.scalar(
        select(func.count())
        .select_from(Product)
        .outerjoin(latest, latest.c.product_id == Product.id)
        .where(Product.is_active.is_(True), latest.c.product_id.is_(None))
    ) or 0
    active_category_count = db.scalar(
        select(func.count()).select_from(Category).where(Category.is_active.is_(True))
    ) or 0
    active_vendor_count = db.scalar(
        select(func.count()).select_from(Vendor).where(Vendor.is_active.is_(True))
    ) or 0
    total_submitted = db.scalar(
        select(func.count())
        .select_from(InventoryCount)
        .where(InventoryCount.status == InventoryCountStatus.SUBMITTED)
    ) or 0

    recent_rows = db.execute(
        select(InventoryCount, func.count(InventoryCountItem.id).label("item_count"))
        .outerjoin(InventoryCountItem)
        .where(InventoryCount.status == InventoryCountStatus.SUBMITTED)
        .group_by(InventoryCount.id)
        .options(selectinload(InventoryCount.submitted_by))
        .order_by(InventoryCount.submitted_at.desc(), InventoryCount.id.desc())
        .limit(5)
    ).all()
    recent_counts = [
        RecentCountSummary(
            id=inventory_count.id,
            submitted_at=inventory_count.submitted_at,
            submitted_by=UserSummary.model_validate(inventory_count.submitted_by),
            item_count=item_count,
        )
        for inventory_count, item_count in recent_rows
    ]

    low_statement, _ = low_stock_statement()
    low_rows = db.execute(
        low_statement.options(
            selectinload(Product.category),
            selectinload(Product.preferred_vendor),
        ).limit(5)
    ).all()
    low_stock_preview = [
        low_stock_response(product, quantity, submitted_at)
        for product, quantity, submitted_at in low_rows
    ]

    return DashboardSummary(
        active_product_count=active_product_count,
        low_stock_product_count=low_stock_product_count,
        uncounted_active_product_count=uncounted_active_product_count,
        active_category_count=active_category_count,
        active_vendor_count=active_vendor_count,
        total_submitted_count_sessions=total_submitted,
        recent_submitted_count_sessions=recent_counts,
        prioritized_low_stock=low_stock_preview,
    )
