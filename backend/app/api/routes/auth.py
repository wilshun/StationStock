from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.auth.dependencies import CurrentUser
from app.auth.passwords import hash_password, verify_password
from app.auth.rate_limit import login_rate_limiter, utc_now
from app.auth.schemas import LoginRequest, LogoutResponse, PasswordChangeRequest, UserResponse
from app.auth.service import authenticate_user
from app.auth.tokens import create_access_token
from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.services.audit import record_audit


router = APIRouter(prefix="/v1/auth", tags=["authentication"])


@router.post("/login", response_model=UserResponse)
def login(
    credentials: LoginRequest,
    request: Request,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> UserResponse:
    key = f"{request.client.host if request.client else 'unknown'}:{credentials.email.strip().lower()}"
    now = utc_now()
    if login_rate_limiter.is_blocked(key, now=now, window_seconds=settings.login_window_seconds):
        raise HTTPException(status_code=429, detail="Too many login attempts; try again shortly")
    user = authenticate_user(db, credentials.email, credentials.password)
    if user is None:
        login_rate_limiter.failure(key, now=now, max_attempts=settings.login_max_attempts, cooldown_seconds=settings.login_cooldown_seconds)
        record_audit(db, "auth.login_failure", "user", metadata={"email": credentials.email.strip().lower()})
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    login_rate_limiter.success(key)
    record_audit(db, "auth.login_success", "user", actor_user_id=user.id, target_id=user.id)
    db.commit()
    token = create_access_token(user.id, auth_version=user.auth_version, settings=settings)
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
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> LogoutResponse:
    record_audit(db, "auth.logout", "user", actor_user_id=current_user.id, target_id=current_user.id)
    db.commit()
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


@router.post("/change-password", response_model=LogoutResponse)
def change_password(
    payload: PasswordChangeRequest,
    response: Response,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> LogoutResponse:
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    current_user.password_hash = hash_password(payload.new_password)
    current_user.auth_version += 1
    record_audit(db, "user.password_changed", "user", actor_user_id=current_user.id, target_id=current_user.id)
    db.commit()
    response.delete_cookie(key=settings.auth_cookie_name, path="/api", secure=settings.auth_cookie_secure, httponly=True, samesite=settings.auth_cookie_samesite)
    return LogoutResponse(status="ok")
