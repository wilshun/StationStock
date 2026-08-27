import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.api.schemas.common import Page, PaginationParams
from app.api.schemas.products import (
    ProductCountHistoryItem,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)
from app.auth.dependencies import CurrentUser, ManagerUser
from app.db.session import get_db
from app.models import Category, InventoryCount, InventoryCountItem, InventoryCountStatus
from app.models import Product, User, Vendor
from app.services.inventory import (
    latest_inventory_for_product,
    latest_inventory_subquery,
    product_response,
)


router = APIRouter(prefix="/v1/products", tags=["products"])


def get_product_or_404(db: Session, product_id: uuid.UUID) -> Product:
    product = db.scalar(
        select(Product)
        .options(selectinload(Product.category), selectinload(Product.preferred_vendor))
        .where(Product.id == product_id)
    )
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


def validate_category(db: Session, category_id: uuid.UUID) -> Category:
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=400, detail="Category does not exist")
    if not category.is_active:
        raise HTTPException(status_code=400, detail="Category is inactive")
    return category


def validate_vendor(db: Session, vendor_id: uuid.UUID | None) -> Vendor | None:
    if vendor_id is None:
        return None
    vendor = db.get(Vendor, vendor_id)
    if vendor is None:
        raise HTTPException(status_code=400, detail="Preferred vendor does not exist")
    if not vendor.is_active:
        raise HTTPException(status_code=400, detail="Preferred vendor is inactive")
    return vendor


def sku_exists(
    db: Session,
    sku: str,
    *,
    exclude_id: uuid.UUID | None = None,
) -> bool:
    statement = select(Product.id).where(func.lower(Product.sku) == sku.lower())
    if exclude_id is not None:
        statement = statement.where(Product.id != exclude_id)
    return db.scalar(statement) is not None


@router.get("", response_model=Page[ProductResponse])
def list_products(
    _current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends()],
    search: str | None = Query(default=None, min_length=1, max_length=200),
    category_id: uuid.UUID | None = None,
    preferred_vendor_id: uuid.UUID | None = None,
    is_active: bool | None = None,
    is_low_stock: bool | None = None,
    is_counted: bool | None = None,
) -> Page[ProductResponse]:
    latest = latest_inventory_subquery()
    filters = []
    if search:
        term = f"%{search.strip()}%"
        filters.append(or_(Product.name.ilike(term), Product.sku.ilike(term)))
    if category_id is not None:
        filters.append(Product.category_id == category_id)
    if preferred_vendor_id is not None:
        filters.append(Product.preferred_vendor_id == preferred_vendor_id)
    if is_active is not None:
        filters.append(Product.is_active.is_(is_active))
    if is_counted is True:
        filters.append(latest.c.product_id.is_not(None))
    elif is_counted is False:
        filters.append(latest.c.product_id.is_(None))
    if is_low_stock is True:
        filters.extend(
            [
                latest.c.product_id.is_not(None),
                latest.c.quantity < Product.minimum_quantity,
            ]
        )
    elif is_low_stock is False:
        filters.extend(
            [
                latest.c.product_id.is_not(None),
                latest.c.quantity >= Product.minimum_quantity,
            ]
        )

    base = (
        select(Product, latest.c.quantity, latest.c.submitted_at)
        .outerjoin(latest, latest.c.product_id == Product.id)
        .where(*filters)
    )
    total = db.scalar(
        select(func.count()).select_from(
            select(Product.id)
            .outerjoin(latest, latest.c.product_id == Product.id)
            .where(*filters)
            .subquery()
        )
    ) or 0
    rows = db.execute(
        base.options(
            selectinload(Product.category),
            selectinload(Product.preferred_vendor),
        )
        .order_by(Product.sku.asc(), Product.id.asc())
        .offset(pagination.offset)
        .limit(pagination.page_size)
    ).all()
    return Page[ProductResponse].create(
        items=[product_response(product, quantity, counted_at) for product, quantity, counted_at in rows],
        pagination=pagination,
        total=total,
    )


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    _manager: ManagerUser,
    db: Annotated[Session, Depends(get_db)],
) -> ProductResponse:
    if sku_exists(db, payload.sku):
        raise HTTPException(status_code=409, detail="Product SKU already exists")
    validate_category(db, payload.category_id)
    validate_vendor(db, payload.preferred_vendor_id)
    product = Product(**payload.model_dump())
    db.add(product)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Product SKU already exists") from None
    product = get_product_or_404(db, product.id)
    return product_response(product, None, None)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: uuid.UUID,
    _current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> ProductResponse:
    product = get_product_or_404(db, product_id)
    latest = latest_inventory_for_product(db, product_id)
    return product_response(
        product,
        latest.quantity if latest else None,
        latest.submitted_at if latest else None,
    )


@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: uuid.UUID,
    payload: ProductUpdate,
    _manager: ManagerUser,
    db: Annotated[Session, Depends(get_db)],
) -> ProductResponse:
    product = get_product_or_404(db, product_id)
    changes = payload.model_dump(exclude_unset=True)
    if payload.sku is not None and sku_exists(db, payload.sku, exclude_id=product.id):
        raise HTTPException(status_code=409, detail="Product SKU already exists")
    if payload.category_id is not None:
        validate_category(db, payload.category_id)
    if "preferred_vendor_id" in payload.model_fields_set:
        validate_vendor(db, payload.preferred_vendor_id)

    final_minimum = changes.get("minimum_quantity", product.minimum_quantity)
    final_target = changes.get("target_quantity", product.target_quantity)
    if final_target < final_minimum:
        raise HTTPException(
            status_code=422,
            detail="target_quantity must be at least minimum_quantity",
        )
    for field, value in changes.items():
        setattr(product, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Product SKU already exists") from None
    product = get_product_or_404(db, product.id)
    latest = latest_inventory_for_product(db, product.id)
    return product_response(
        product,
        latest.quantity if latest else None,
        latest.submitted_at if latest else None,
    )


@router.get("/{product_id}/count-history", response_model=Page[ProductCountHistoryItem])
def get_product_count_history(
    product_id: uuid.UUID,
    _current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends()],
) -> Page[ProductCountHistoryItem]:
    get_product_or_404(db, product_id)
    filters = (
        InventoryCountItem.product_id == product_id,
        InventoryCount.status == InventoryCountStatus.SUBMITTED,
    )
    total = db.scalar(
        select(func.count())
        .select_from(InventoryCountItem)
        .join(InventoryCount)
        .where(*filters)
    ) or 0
    rows = db.execute(
        select(InventoryCountItem, InventoryCount, User)
        .select_from(InventoryCountItem)
        .join(
            InventoryCount,
            InventoryCount.id == InventoryCountItem.inventory_count_id,
        )
        .join(User, User.id == InventoryCount.submitted_by_user_id)
        .where(*filters)
        .order_by(InventoryCount.submitted_at.desc(), InventoryCount.id.desc())
        .offset(pagination.offset)
        .limit(pagination.page_size)
    ).all()
    items = [
        ProductCountHistoryItem(
            count_id=count.id,
            submitted_at=count.submitted_at,
            quantity=item.quantity,
            submitted_by_user_id=user.id,
            submitted_by_email=user.email,
        )
        for item, count, user in rows
    ]
    return Page[ProductCountHistoryItem].create(
        items=items,
        pagination=pagination,
        total=total,
    )
