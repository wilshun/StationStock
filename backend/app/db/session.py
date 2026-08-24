from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


class DatabaseNotConfiguredError(RuntimeError):
    """Raised when database access is requested without a DATABASE_URL."""


@lru_cache
def get_engine() -> Engine:
    database_url = get_settings().database_url
    if not database_url:
        raise DatabaseNotConfiguredError("DATABASE_URL is not configured")

    return create_engine(database_url, pool_pre_ping=True)


SessionLocal = sessionmaker(autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    with SessionLocal(bind=get_engine()) as session:
        yield session
