import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_production_rejects_development_auth_secret() -> None:
    with pytest.raises(ValidationError, match="AUTH_SECRET_KEY must be changed"):
        Settings(_env_file=None, environment="production")


def test_production_forces_secure_auth_cookie() -> None:
    settings = Settings(
        _env_file=None,
        environment="production",
        AUTH_SECRET_KEY="a-unique-production-style-secret-for-this-test",
        AUTH_COOKIE_SECURE=False,
    )

    assert settings.auth_cookie_secure is True
