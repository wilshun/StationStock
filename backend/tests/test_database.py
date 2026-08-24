import pytest
from sqlalchemy import text

from app.core.config import get_settings
from app.db.session import get_engine


@pytest.mark.skipif(
    not get_settings().database_url,
    reason="DATABASE_URL is not configured",
)
def test_database_connectivity() -> None:
    with get_engine().connect() as connection:
        assert connection.scalar(text("SELECT 1")) == 1
