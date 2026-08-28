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

    environment: str = "development"
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

    @model_validator(mode="after")
    def enforce_production_auth_safety(self) -> "Settings":
        if self.environment.lower() == "production":
            if self.auth_secret_key.get_secret_value() == "development-only-change-me-use-32-bytes":
                raise ValueError("AUTH_SECRET_KEY must be changed in production")
            self.auth_cookie_secure = True
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
