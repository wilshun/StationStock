"""complete core mvp schema

Revision ID: 0de475186ebf
Revises: 797a680c2300
Create Date: 2026-08-27 15:39:07.663992
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0de475186ebf"
down_revision: str | None = "797a680c2300"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index("ix_users_role", "users", ["role"])
    op.create_index("ix_users_is_active", "users", ["is_active"])

    op.add_column("categories", sa.Column("description", sa.Text(), nullable=True))
    op.create_index("ix_categories_is_active", "categories", ["is_active"])
    op.create_index(
        "uq_categories_name_lower",
        "categories",
        [sa.literal_column("lower(name)")],
        unique=True,
    )

    op.add_column(
        "vendors",
        sa.Column("contact_name", sa.String(length=200), nullable=True),
    )
    op.add_column("vendors", sa.Column("phone", sa.String(length=50), nullable=True))
    op.add_column("vendors", sa.Column("email", sa.String(length=320), nullable=True))
    op.add_column("vendors", sa.Column("notes", sa.Text(), nullable=True))
    op.create_index("ix_vendors_is_active", "vendors", ["is_active"])
    op.create_index(
        "uq_vendors_name_lower",
        "vendors",
        [sa.literal_column("lower(name)")],
        unique=True,
    )

    op.add_column("products", sa.Column("description", sa.Text(), nullable=True))
    op.add_column(
        "products",
        sa.Column("unit_description", sa.String(length=100), nullable=True),
    )
    op.create_index("ix_products_is_active", "products", ["is_active"])
    op.create_index(
        "uq_products_sku_lower",
        "products",
        [sa.literal_column("lower(sku)")],
        unique=True,
    )

    inventory_count_status = postgresql.ENUM(
        "draft",
        "submitted",
        name="inventory_count_status",
        create_type=False,
    )
    inventory_count_status.create(op.get_bind(), checkfirst=False)
    op.add_column(
        "inventory_counts",
        sa.Column(
            "status",
            inventory_count_status,
            server_default="submitted",
            nullable=False,
        ),
    )
    op.drop_index(
        "ix_inventory_counts_counted_by_id",
        table_name="inventory_counts",
    )
    op.drop_constraint(
        "fk_inventory_counts_counted_by_id_users",
        "inventory_counts",
        type_="foreignkey",
    )
    op.alter_column(
        "inventory_counts",
        "counted_by_id",
        new_column_name="started_by_user_id",
        existing_type=sa.Uuid(),
        existing_nullable=False,
    )
    op.create_foreign_key(
        "fk_inventory_counts_started_by_user_id_users",
        "inventory_counts",
        "users",
        ["started_by_user_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index(
        "ix_inventory_counts_started_by_user_id",
        "inventory_counts",
        ["started_by_user_id"],
    )
    op.add_column(
        "inventory_counts",
        sa.Column("submitted_by_user_id", sa.Uuid(), nullable=True),
    )
    op.add_column(
        "inventory_counts",
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.execute(
        """
        UPDATE inventory_counts
        SET submitted_by_user_id = started_by_user_id,
            submitted_at = created_at
        """
    )
    op.create_foreign_key(
        "fk_inventory_counts_submitted_by_user_id_users",
        "inventory_counts",
        "users",
        ["submitted_by_user_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index(
        "ix_inventory_counts_submitted_by_user_id",
        "inventory_counts",
        ["submitted_by_user_id"],
    )
    op.create_index(
        "ix_inventory_counts_submitted_at",
        "inventory_counts",
        ["submitted_at"],
    )
    op.create_index(
        "ix_inventory_counts_status",
        "inventory_counts",
        ["status"],
    )
    op.alter_column(
        "inventory_counts",
        "status",
        existing_type=inventory_count_status,
        server_default="draft",
        existing_nullable=False,
    )

    op.add_column(
        "inventory_count_items",
        sa.Column("notes", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("inventory_count_items", "notes")

    op.drop_index("ix_inventory_counts_status", table_name="inventory_counts")
    op.drop_index("ix_inventory_counts_submitted_at", table_name="inventory_counts")
    op.drop_index(
        "ix_inventory_counts_submitted_by_user_id",
        table_name="inventory_counts",
    )
    op.drop_constraint(
        "fk_inventory_counts_submitted_by_user_id_users",
        "inventory_counts",
        type_="foreignkey",
    )
    op.drop_column("inventory_counts", "submitted_at")
    op.drop_column("inventory_counts", "submitted_by_user_id")
    op.drop_index(
        "ix_inventory_counts_started_by_user_id",
        table_name="inventory_counts",
    )
    op.drop_constraint(
        "fk_inventory_counts_started_by_user_id_users",
        "inventory_counts",
        type_="foreignkey",
    )
    op.alter_column(
        "inventory_counts",
        "started_by_user_id",
        new_column_name="counted_by_id",
        existing_type=sa.Uuid(),
        existing_nullable=False,
    )
    op.create_foreign_key(
        "fk_inventory_counts_counted_by_id_users",
        "inventory_counts",
        "users",
        ["counted_by_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index(
        "ix_inventory_counts_counted_by_id",
        "inventory_counts",
        ["counted_by_id"],
    )
    op.drop_column("inventory_counts", "status")
    postgresql.ENUM(name="inventory_count_status").drop(
        op.get_bind(),
        checkfirst=False,
    )

    op.drop_index("uq_products_sku_lower", table_name="products")
    op.drop_index("ix_products_is_active", table_name="products")
    op.drop_column("products", "unit_description")
    op.drop_column("products", "description")

    op.drop_index("uq_vendors_name_lower", table_name="vendors")
    op.drop_index("ix_vendors_is_active", table_name="vendors")
    op.drop_column("vendors", "notes")
    op.drop_column("vendors", "email")
    op.drop_column("vendors", "phone")
    op.drop_column("vendors", "contact_name")

    op.drop_index("uq_categories_name_lower", table_name="categories")
    op.drop_index("ix_categories_is_active", table_name="categories")
    op.drop_column("categories", "description")

    op.drop_index("ix_users_is_active", table_name="users")
    op.drop_index("ix_users_role", table_name="users")
