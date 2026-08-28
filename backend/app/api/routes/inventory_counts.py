import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.api.schemas.common import Page, PaginationParams
from app.api.schemas.inventory_counts import (
    InventoryCountCreate,
    InventoryCountItemResponse,
    InventoryCountItemUpsert,
    InventoryCountListItem,
    InventoryCountResponse,
    InventoryCountUpdate,
    UserSummary,
)
from app.api.schemas.products import ProductSummary
from app.auth.dependencies import CurrentUser
from app.db.session import get_db
from app.models import (
    InventoryCount,
    InventoryCountItem,
    InventoryCountStatus,
    Product,
    User,
    UserRole,
)
from app.services.inventory_counts import (
    EmptyInventoryCountError,
    submit_inventory_count as submit_inventory_count_service,
)
from app.services.audit import record_audit


router = APIRouter(prefix="/v1/inventory-counts", tags=["inventory counts"])


def inventory_count_options():
    return (
        selectinload(InventoryCount.started_by),
        selectinload(InventoryCount.submitted_by),
        selectinload(InventoryCount.items).selectinload(InventoryCountItem.product),
    )


def get_count_or_404(db: Session, count_id: uuid.UUID) -> InventoryCount:
    inventory_count = db.scalar(
        select(InventoryCount)
        .options(*inventory_count_options())
        .where(InventoryCount.id == count_id)
    )
    if inventory_count is None:
        raise HTTPException(status_code=404, detail="Inventory count not found")
    return inventory_count


def ensure_draft_editor(inventory_count: InventoryCount, user: User) -> None:
    if inventory_count.status is not InventoryCountStatus.DRAFT:
        raise HTTPException(status_code=409, detail="Submitted counts are read-only")
    if inventory_count.started_by_user_id != user.id and user.role is not UserRole.MANAGER:
        raise HTTPException(
            status_code=403,
            detail="Only the count owner or a manager may edit this draft",
        )


def count_response(inventory_count: InventoryCount) -> InventoryCountResponse:
    return InventoryCountResponse(
        id=inventory_count.id,
        status=inventory_count.status,
        started_by=UserSummary.model_validate(inventory_count.started_by),
        submitted_by=(
            UserSummary.model_validate(inventory_count.submitted_by)
            if inventory_count.submitted_by is not None
            else None
        ),
        notes=inventory_count.notes,
        submitted_at=inventory_count.submitted_at,
        created_at=inventory_count.created_at,
        updated_at=inventory_count.updated_at,
        items=[
            InventoryCountItemResponse(
                id=item.id,
                product=ProductSummary.model_validate(item.product),
                quantity=item.quantity,
                notes=item.notes,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            for item in sorted(inventory_count.items, key=lambda value: value.product.sku)
        ],
    )


@router.get("", response_model=Page[InventoryCountListItem])
def list_inventory_counts(
    _current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends()],
    inventory_status: InventoryCountStatus | None = Query(default=None, alias="status"),
    user_id: uuid.UUID | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> Page[InventoryCountListItem]:
    if date_from and date_to and date_from > date_to:
        raise HTTPException(status_code=400, detail="date_from must not be after date_to")
    filters = []
    if inventory_status is not None:
        filters.append(InventoryCount.status == inventory_status)
    if user_id is not None:
        filters.append(InventoryCount.started_by_user_id == user_id)
    if date_from is not None:
        filters.append(InventoryCount.created_at >= date_from)
    if date_to is not None:
        filters.append(InventoryCount.created_at <= date_to)

    total = db.scalar(
        select(func.count()).select_from(InventoryCount).where(*filters)
    ) or 0
    rows = db.execute(
        select(InventoryCount, func.count(InventoryCountItem.id).label("item_count"))
        .outerjoin(InventoryCountItem)
        .where(*filters)
        .group_by(InventoryCount.id)
        .options(
            selectinload(InventoryCount.started_by),
            selectinload(InventoryCount.submitted_by),
        )
        .order_by(InventoryCount.created_at.desc(), InventoryCount.id.desc())
        .offset(pagination.offset)
        .limit(pagination.page_size)
    ).all()
    items = [
        InventoryCountListItem(
            id=inventory_count.id,
            status=inventory_count.status,
            started_by=UserSummary.model_validate(inventory_count.started_by),
            submitted_by=(
                UserSummary.model_validate(inventory_count.submitted_by)
                if inventory_count.submitted_by is not None
                else None
            ),
            notes=inventory_count.notes,
            submitted_at=inventory_count.submitted_at,
            created_at=inventory_count.created_at,
            updated_at=inventory_count.updated_at,
            item_count=item_count,
        )
        for inventory_count, item_count in rows
    ]
    return Page[InventoryCountListItem].create(
        items=items,
        pagination=pagination,
        total=total,
    )


@router.post("", response_model=InventoryCountResponse, status_code=status.HTTP_201_CREATED)
def create_inventory_count(
    payload: InventoryCountCreate,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> InventoryCountResponse:
    inventory_count = InventoryCount(started_by=current_user, notes=payload.notes)
    db.add(inventory_count)
    db.commit()
    return count_response(get_count_or_404(db, inventory_count.id))


@router.get("/{count_id}", response_model=InventoryCountResponse)
def get_inventory_count(
    count_id: uuid.UUID,
    _current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> InventoryCountResponse:
    return count_response(get_count_or_404(db, count_id))


@router.patch("/{count_id}", response_model=InventoryCountResponse)
def update_inventory_count(
    count_id: uuid.UUID,
    payload: InventoryCountUpdate,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> InventoryCountResponse:
    inventory_count = get_count_or_404(db, count_id)
    ensure_draft_editor(inventory_count, current_user)
    inventory_count.notes = payload.notes
    db.commit()
    return count_response(get_count_or_404(db, count_id))


@router.put("/{count_id}/items/{product_id}", response_model=InventoryCountResponse)
def upsert_inventory_count_item(
    count_id: uuid.UUID,
    product_id: uuid.UUID,
    payload: InventoryCountItemUpsert,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> InventoryCountResponse:
    inventory_count = get_count_or_404(db, count_id)
    ensure_draft_editor(inventory_count, current_user)
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    if not product.is_active:
        raise HTTPException(status_code=400, detail="Inactive products cannot be counted")

    item = db.scalar(
        select(InventoryCountItem).where(
            InventoryCountItem.inventory_count_id == count_id,
            InventoryCountItem.product_id == product_id,
        )
    )
    if item is None:
        item = InventoryCountItem(
            inventory_count=inventory_count,
            product=product,
            quantity=payload.quantity,
            notes=payload.notes,
        )
        db.add(item)
    else:
        item.quantity = payload.quantity
        item.notes = payload.notes
    db.commit()
    return count_response(get_count_or_404(db, count_id))


@router.delete("/{count_id}/items/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_inventory_count_item(
    count_id: uuid.UUID,
    product_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    inventory_count = get_count_or_404(db, count_id)
    ensure_draft_editor(inventory_count, current_user)
    item = db.scalar(
        select(InventoryCountItem).where(
            InventoryCountItem.inventory_count_id == count_id,
            InventoryCountItem.product_id == product_id,
        )
    )
    if item is None:
        raise HTTPException(status_code=404, detail="Inventory count item not found")
    db.delete(item)
    db.commit()


@router.post("/{count_id}/submit", response_model=InventoryCountResponse)
def submit_inventory_count(
    count_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> InventoryCountResponse:
    inventory_count = get_count_or_404(db, count_id)
    ensure_draft_editor(inventory_count, current_user)
    try:
        submit_inventory_count_service(inventory_count, current_user)
        record_audit(db, "inventory_count.submitted", "inventory_count", actor_user_id=current_user.id, target_id=inventory_count.id, metadata={"item_count": len(inventory_count.items)})
        db.commit()
    except EmptyInventoryCountError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from None
    except Exception:
        db.rollback()
        raise
    return count_response(get_count_or_404(db, count_id))
