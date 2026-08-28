from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        env_prefix="STATIONSTOCK_",
        extra="ignore",
    )

    environment: Literal["development", "test", "production"] = Field(
        default="development", validation_alias="ENVIRONMENT"
    )
    app_name: str = "StationStock API"
    database_url: str | None = Field(default=None, validation_alias="DATABASE_URL")
    auth_secret_key: SecretStr = Field(
        default=SecretStr("development-only-change-me-use-32-bytes"),
        validation_alias="AUTH_SECRET_KEY",
    )
    access_token_expire_minutes: int = Field(
        default=15,
        gt=0,
        validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES",
    )
    auth_cookie_name: str = Field(
        default="stationstock_access_token",
        validation_alias="AUTH_COOKIE_NAME",
    )
    auth_cookie_secure: bool = Field(
        default=False,
        validation_alias="AUTH_COOKIE_SECURE",
    )
    auth_cookie_samesite: Literal["lax", "strict", "none"] = Field(
        default="lax",
        validation_alias="AUTH_COOKIE_SAMESITE",
    )
    allowed_frontend_origin: str = Field(
        default="http://localhost:3000",
        validation_alias="ALLOWED_FRONTEND_ORIGIN",
    )
    api_docs_enabled: bool | None = Field(default=None, validation_alias="API_DOCS_ENABLED")
    login_max_attempts: int = Field(default=5, ge=2, le=20, validation_alias="LOGIN_MAX_ATTEMPTS")
    login_window_seconds: int = Field(default=300, ge=30, le=3600, validation_alias="LOGIN_WINDOW_SECONDS")
    login_cooldown_seconds: int = Field(default=60, ge=1, le=900, validation_alias="LOGIN_COOLDOWN_SECONDS")

    @property
    def docs_enabled(self) -> bool:
        return self.api_docs_enabled if self.api_docs_enabled is not None else self.environment != "production"

    @model_validator(mode="after")
    def enforce_production_auth_safety(self) -> "Settings":
        if self.environment == "production":
            secret = self.auth_secret_key.get_secret_value()
            if not self.database_url:
                raise ValueError("DATABASE_URL is required in production")
            if secret == "development-only-change-me-use-32-bytes" or len(secret) < 32:
                raise ValueError("AUTH_SECRET_KEY must be a unique value of at least 32 characters in production")
            if not self.auth_cookie_secure:
                raise ValueError("AUTH_COOKIE_SECURE must be true in production")
            if not self.allowed_frontend_origin.startswith("https://"):
                raise ValueError("ALLOWED_FRONTEND_ORIGIN must be a single HTTPS origin in production")
        if "*" in self.allowed_frontend_origin:
            raise ValueError("Wildcard frontend origins are not allowed with credentials")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
