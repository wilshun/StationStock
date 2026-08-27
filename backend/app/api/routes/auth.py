from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.auth.dependencies import CurrentUser
from app.auth.schemas import LoginRequest, LogoutResponse, UserResponse
from app.auth.service import authenticate_user
from app.auth.tokens import create_access_token
from app.core.config import Settings, get_settings
from app.db.session import get_db


router = APIRouter(prefix="/v1/auth", tags=["authentication"])


@router.post("/login", response_model=UserResponse)
def login(
    credentials: LoginRequest,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> UserResponse:
    user = authenticate_user(db, credentials.email, credentials.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(user.id, settings=settings)
    response.set_cookie(
        key=settings.auth_cookie_name,
        value=token,
        max_age=settings.access_token_expire_minutes * 60,
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite=settings.auth_cookie_samesite,
        path="/api",
    )
    return UserResponse.model_validate(user)


@router.post("/logout", response_model=LogoutResponse)
def logout(
    response: Response,
    settings: Annotated[Settings, Depends(get_settings)],
) -> LogoutResponse:
    response.delete_cookie(
        key=settings.auth_cookie_name,
        path="/api",
        secure=settings.auth_cookie_secure,
        httponly=True,
        samesite=settings.auth_cookie_samesite,
    )
    return LogoutResponse(status="ok")


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: CurrentUser) -> UserResponse:
    return UserResponse.model_validate(current_user)
