import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_production_rejects_development_auth_secret() -> None:
    with pytest.raises(ValidationError, match="DATABASE_URL is required"):
        Settings(_env_file=None, ENVIRONMENT="production")


def test_production_forces_secure_auth_cookie() -> None:
    settings = Settings(
        _env_file=None,
        ENVIRONMENT="production",
        DATABASE_URL="postgresql+psycopg://user:password@db/stationstock",
        AUTH_SECRET_KEY="a-unique-production-style-secret-for-this-test",
        AUTH_COOKIE_SECURE=True,
        ALLOWED_FRONTEND_ORIGIN="https://inventory.example.com",
    )

    assert settings.auth_cookie_secure is True
