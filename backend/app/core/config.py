from functools import lru_cache
from pathlib import Path

from pydantic import Field
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


@lru_cache
def get_settings() -> Settings:
    return Settings()
