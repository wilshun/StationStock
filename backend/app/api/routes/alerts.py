import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.api.schemas.common import Page, PaginationParams
from app.api.schemas.dashboard import LowStockItem
from app.auth.dependencies import CurrentUser
from app.db.session import get_db
from app.models import Product
from app.services.inventory import low_stock_response, low_stock_statement


router = APIRouter(prefix="/v1/alerts", tags=["alerts"])


@router.get("/low-stock", response_model=Page[LowStockItem])
def list_low_stock_alerts(
    _current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends()],
    category_id: uuid.UUID | None = None,
    preferred_vendor_id: uuid.UUID | None = None,
) -> Page[LowStockItem]:
    statement, _latest = low_stock_statement()
    if category_id is not None:
        statement = statement.where(Product.category_id == category_id)
    if preferred_vendor_id is not None:
        statement = statement.where(Product.preferred_vendor_id == preferred_vendor_id)

    count_statement = select(func.count()).select_from(
        statement.order_by(None).with_only_columns(Product.id).subquery()
    )
    total = db.scalar(count_statement) or 0
    rows = db.execute(
        statement.options(
            selectinload(Product.category),
            selectinload(Product.preferred_vendor),
        )
        .offset(pagination.offset)
        .limit(pagination.page_size)
    ).all()
    return Page[LowStockItem].create(
        items=[
            low_stock_response(product, quantity, submitted_at)
            for product, quantity, submitted_at in rows
        ],
        pagination=pagination,
        total=total,
    )
