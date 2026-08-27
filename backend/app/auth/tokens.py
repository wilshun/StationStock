import uuid
from datetime import UTC, datetime, timedelta

import jwt

from app.core.config import Settings, get_settings


class InvalidAccessTokenError(ValueError):
    """Raised when an access token is invalid or expired."""


def create_access_token(
    user_id: uuid.UUID,
    *,
    settings: Settings | None = None,
    expires_delta: timedelta | None = None,
    now: datetime | None = None,
) -> str:
    auth_settings = settings or get_settings()
    issued_at = now or datetime.now(UTC)
    expires_at = issued_at + (
        expires_delta
        or timedelta(minutes=auth_settings.access_token_expire_minutes)
    )
    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": issued_at,
        "exp": expires_at,
    }
    return jwt.encode(
        payload,
        auth_settings.auth_secret_key.get_secret_value(),
        algorithm="HS256",
    )


def decode_access_token(
    token: str,
    *,
    settings: Settings | None = None,
) -> uuid.UUID:
    auth_settings = settings or get_settings()
    try:
        payload = jwt.decode(
            token,
            auth_settings.auth_secret_key.get_secret_value(),
            algorithms=["HS256"],
            options={"require": ["sub", "type", "iat", "exp"]},
        )
        if payload["type"] != "access":
            raise InvalidAccessTokenError("Unexpected token type")
        return uuid.UUID(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError) as exc:
        raise InvalidAccessTokenError("Invalid or expired access token") from exc
