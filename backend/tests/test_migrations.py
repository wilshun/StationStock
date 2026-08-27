from io import StringIO
from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory

from app.core.config import get_settings


BACKEND_DIR = Path(__file__).resolve().parents[1]


def make_alembic_config(*, output_buffer: StringIO | None = None) -> Config:
    return Config(
        str(BACKEND_DIR / "alembic.ini"),
        output_buffer=output_buffer,
    )


def test_authentication_migration_is_the_only_head() -> None:
    script = ScriptDirectory.from_config(make_alembic_config())

    assert script.get_heads() == ["797a680c2300"]


def test_initial_migration_generates_core_schema_sql(monkeypatch) -> None:
    output = StringIO()
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://stationstock:test@localhost:5432/stationstock_test",
    )
    get_settings.cache_clear()

    try:
        command.upgrade(make_alembic_config(output_buffer=output), "head", sql=True)
    finally:
        get_settings.cache_clear()

    migration_sql = output.getvalue()
    for table_name in (
        "users",
        "categories",
        "vendors",
        "products",
        "inventory_counts",
        "inventory_count_items",
    ):
        assert f"CREATE TABLE {table_name}" in migration_sql

    assert "uq_products_sku" in migration_sql
    assert "uq_categories_name" in migration_sql
    assert "uq_vendors_name" in migration_sql
    assert "ck_products_minimum_quantity_nonnegative" in migration_sql
    assert "ck_products_target_quantity_at_least_minimum" in migration_sql
    assert "ck_inventory_count_items_quantity_nonnegative" in migration_sql
    assert "uq_inventory_count_items_count_product" in migration_sql
    assert "ADD COLUMN password_hash VARCHAR(255)" in migration_sql
    assert "CREATE UNIQUE INDEX uq_users_email_lower" in migration_sql


def test_authentication_migration_generates_downgrade_sql(monkeypatch) -> None:
    output = StringIO()
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://stationstock:test@localhost:5432/stationstock_test",
    )
    get_settings.cache_clear()

    try:
        command.downgrade(
            make_alembic_config(output_buffer=output),
            "797a680c2300:a5bfce1c4424",
            sql=True,
        )
    finally:
        get_settings.cache_clear()

    migration_sql = output.getvalue()
    assert "DROP INDEX uq_users_email_lower" in migration_sql
    assert "ALTER TABLE users DROP COLUMN password_hash" in migration_sql
