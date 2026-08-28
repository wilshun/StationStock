from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.auth.service import get_user_by_id
from app.auth.tokens import InvalidAccessTokenError, decode_access_token
from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.models.user import User, UserRole


def authentication_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )


def get_current_user(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> User:
    token = request.cookies.get(settings.auth_cookie_name)
    if not token:
        raise authentication_error()

    try:
        user_id, auth_version = decode_access_token(token, settings=settings)
    except InvalidAccessTokenError:
        raise authentication_error() from None

    user = get_user_by_id(db, user_id)
    if user is None or not user.is_active or user.auth_version != auth_version:
        raise authentication_error()
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_manager(current_user: CurrentUser) -> User:
    if current_user.role is not UserRole.MANAGER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required",
        )
    return current_user


ManagerUser = Annotated[User, Depends(require_manager)]
