import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.schemas.common import Page, PaginationParams
from app.api.schemas.users import UserAdminResponse, UserCreate, UserUpdate
from app.auth.dependencies import ManagerUser
from app.auth.passwords import hash_password
from app.auth.service import get_user_by_email
from app.db.session import get_db
from app.models import User, UserRole


router = APIRouter(prefix="/v1/users", tags=["users"])


def get_user_or_404(db: Session, user_id: uuid.UUID) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("", response_model=Page[UserAdminResponse])
def list_users(
    _manager: ManagerUser,
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends()],
    role: UserRole | None = None,
    is_active: bool | None = None,
    search: str | None = Query(default=None, min_length=1, max_length=320),
) -> Page[UserAdminResponse]:
    filters = []
    if role is not None:
        filters.append(User.role == role)
    if is_active is not None:
        filters.append(User.is_active.is_(is_active))
    if search:
        filters.append(User.email.ilike(f"%{search.strip()}%"))

    total = db.scalar(select(func.count()).select_from(User).where(*filters)) or 0
    users = db.scalars(
        select(User)
        .where(*filters)
        .order_by(User.email.asc(), User.id.asc())
        .offset(pagination.offset)
        .limit(pagination.page_size)
    ).all()
    return Page[UserAdminResponse].create(
        items=[UserAdminResponse.model_validate(user) for user in users],
        pagination=pagination,
        total=total,
    )


@router.post("", response_model=UserAdminResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    _manager: ManagerUser,
    db: Annotated[Session, Depends(get_db)],
) -> UserAdminResponse:
    if get_user_by_email(db, payload.email) is not None:
        raise HTTPException(status_code=409, detail="Email already exists")

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        role=payload.role,
        is_active=payload.is_active,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already exists") from None
    db.refresh(user)
    return UserAdminResponse.model_validate(user)


@router.get("/{user_id}", response_model=UserAdminResponse)
def get_user(
    user_id: uuid.UUID,
    _manager: ManagerUser,
    db: Annotated[Session, Depends(get_db)],
) -> UserAdminResponse:
    return UserAdminResponse.model_validate(get_user_or_404(db, user_id))


@router.patch("/{user_id}", response_model=UserAdminResponse)
def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    manager: ManagerUser,
    db: Annotated[Session, Depends(get_db)],
) -> UserAdminResponse:
    user = get_user_or_404(db, user_id)
    if user.id == manager.id:
        locks_self_out = payload.is_active is False or (
            payload.role is not None and payload.role is not UserRole.MANAGER
        )
        if locks_self_out:
            raise HTTPException(
                status_code=400,
                detail="Managers cannot deactivate or demote their own account",
            )

    if payload.role is not None:
        user.role = payload.role
    if payload.is_active is not None:
        user.is_active = payload.is_active
    if payload.password is not None:
        user.password_hash = hash_password(payload.password)
    db.commit()
    db.refresh(user)
    return UserAdminResponse.model_validate(user)
