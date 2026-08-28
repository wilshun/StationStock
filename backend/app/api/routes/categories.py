import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.schemas.categories import CategoryCreate, CategoryResponse, CategoryUpdate
from app.api.schemas.common import Page, PaginationParams
from app.auth.dependencies import CurrentUser, ManagerUser
from app.db.session import get_db
from app.models import Category
from app.services.audit import record_audit


router = APIRouter(prefix="/v1/categories", tags=["categories"])


def get_category_or_404(db: Session, category_id: uuid.UUID) -> Category:
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


def category_name_exists(
    db: Session,
    name: str,
    *,
    exclude_id: uuid.UUID | None = None,
) -> bool:
    statement = select(Category.id).where(func.lower(Category.name) == name.lower())
    if exclude_id is not None:
        statement = statement.where(Category.id != exclude_id)
    return db.scalar(statement) is not None


@router.get("", response_model=Page[CategoryResponse])
def list_categories(
    _current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends()],
    search: str | None = Query(default=None, min_length=1, max_length=120),
    is_active: bool | None = None,
) -> Page[CategoryResponse]:
    filters = []
    if search:
        filters.append(Category.name.ilike(f"%{search.strip()}%"))
    if is_active is not None:
        filters.append(Category.is_active.is_(is_active))
    total = db.scalar(select(func.count()).select_from(Category).where(*filters)) or 0
    categories = db.scalars(
        select(Category)
        .where(*filters)
        .order_by(Category.name.asc(), Category.id.asc())
        .offset(pagination.offset)
        .limit(pagination.page_size)
    ).all()
    return Page[CategoryResponse].create(
        items=[CategoryResponse.model_validate(item) for item in categories],
        pagination=pagination,
        total=total,
    )


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate,
    manager: ManagerUser,
    db: Annotated[Session, Depends(get_db)],
) -> CategoryResponse:
    if category_name_exists(db, payload.name):
        raise HTTPException(status_code=409, detail="Category name already exists")
    category = Category(name=payload.name, description=payload.description)
    db.add(category)
    db.flush()
    record_audit(db, "category.created", "category", actor_user_id=manager.id, target_id=category.id)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Category name already exists") from None
    db.refresh(category)
    return CategoryResponse.model_validate(category)


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: uuid.UUID,
    _current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> CategoryResponse:
    return CategoryResponse.model_validate(get_category_or_404(db, category_id))


@router.patch("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: uuid.UUID,
    payload: CategoryUpdate,
    manager: ManagerUser,
    db: Annotated[Session, Depends(get_db)],
) -> CategoryResponse:
    category = get_category_or_404(db, category_id)
    if payload.name is not None:
        if category_name_exists(db, payload.name, exclude_id=category.id):
            raise HTTPException(status_code=409, detail="Category name already exists")
        category.name = payload.name
    for field in ("description", "is_active"):
        if field in payload.model_fields_set:
            setattr(category, field, getattr(payload, field))
    record_audit(db, "category.updated", "category", actor_user_id=manager.id, target_id=category.id)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Category name already exists") from None
    db.refresh(category)
    return CategoryResponse.model_validate(category)
