import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.schemas.common import Page, PaginationParams
from app.api.schemas.vendors import VendorCreate, VendorResponse, VendorUpdate
from app.auth.dependencies import CurrentUser, ManagerUser
from app.db.session import get_db
from app.models import Vendor


router = APIRouter(prefix="/v1/vendors", tags=["vendors"])


def get_vendor_or_404(db: Session, vendor_id: uuid.UUID) -> Vendor:
    vendor = db.get(Vendor, vendor_id)
    if vendor is None:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor


def vendor_name_exists(
    db: Session,
    name: str,
    *,
    exclude_id: uuid.UUID | None = None,
) -> bool:
    statement = select(Vendor.id).where(func.lower(Vendor.name) == name.lower())
    if exclude_id is not None:
        statement = statement.where(Vendor.id != exclude_id)
    return db.scalar(statement) is not None


@router.get("", response_model=Page[VendorResponse])
def list_vendors(
    _current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends()],
    search: str | None = Query(default=None, min_length=1, max_length=200),
    is_active: bool | None = None,
) -> Page[VendorResponse]:
    filters = []
    if search:
        filters.append(Vendor.name.ilike(f"%{search.strip()}%"))
    if is_active is not None:
        filters.append(Vendor.is_active.is_(is_active))
    total = db.scalar(select(func.count()).select_from(Vendor).where(*filters)) or 0
    vendors = db.scalars(
        select(Vendor)
        .where(*filters)
        .order_by(Vendor.name.asc(), Vendor.id.asc())
        .offset(pagination.offset)
        .limit(pagination.page_size)
    ).all()
    return Page[VendorResponse].create(
        items=[VendorResponse.model_validate(item) for item in vendors],
        pagination=pagination,
        total=total,
    )


@router.post("", response_model=VendorResponse, status_code=status.HTTP_201_CREATED)
def create_vendor(
    payload: VendorCreate,
    _manager: ManagerUser,
    db: Annotated[Session, Depends(get_db)],
) -> VendorResponse:
    if vendor_name_exists(db, payload.name):
        raise HTTPException(status_code=409, detail="Vendor name already exists")
    vendor = Vendor(**payload.model_dump())
    db.add(vendor)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Vendor name already exists") from None
    db.refresh(vendor)
    return VendorResponse.model_validate(vendor)


@router.get("/{vendor_id}", response_model=VendorResponse)
def get_vendor(
    vendor_id: uuid.UUID,
    _current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> VendorResponse:
    return VendorResponse.model_validate(get_vendor_or_404(db, vendor_id))


@router.patch("/{vendor_id}", response_model=VendorResponse)
def update_vendor(
    vendor_id: uuid.UUID,
    payload: VendorUpdate,
    _manager: ManagerUser,
    db: Annotated[Session, Depends(get_db)],
) -> VendorResponse:
    vendor = get_vendor_or_404(db, vendor_id)
    if payload.name is not None and vendor_name_exists(
        db,
        payload.name,
        exclude_id=vendor.id,
    ):
        raise HTTPException(status_code=409, detail="Vendor name already exists")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(vendor, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Vendor name already exists") from None
    db.refresh(vendor)
    return VendorResponse.model_validate(vendor)
