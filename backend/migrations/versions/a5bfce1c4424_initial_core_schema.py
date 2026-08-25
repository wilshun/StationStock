"""initial core schema

Revision ID: a5bfce1c4424
Revises: 
Create Date: 2026-08-24 19:58:46.332327
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = 'a5bfce1c4424'
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("full_name", sa.String(length=200), nullable=False),
        sa.Column(
            "role",
            sa.Enum("manager", "employee", name="user_role"),
            server_default="employee",
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_table(
        "categories",
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_categories")),
        sa.UniqueConstraint("name", name="uq_categories_name"),
    )
    op.create_table(
        "vendors",
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_vendors")),
        sa.UniqueConstraint("name", name="uq_vendors_name"),
    )
    op.create_table(
        "products",
        sa.Column("sku", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("category_id", sa.Uuid(), nullable=False),
        sa.Column("preferred_vendor_id", sa.Uuid(), nullable=True),
        sa.Column("minimum_quantity", sa.Integer(), server_default="0", nullable=False),
        sa.Column("target_quantity", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "minimum_quantity >= 0",
            name=op.f("ck_products_minimum_quantity_nonnegative"),
        ),
        sa.CheckConstraint(
            "target_quantity >= minimum_quantity",
            name=op.f("ck_products_target_quantity_at_least_minimum"),
        ),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["categories.id"],
            name=op.f("fk_products_category_id_categories"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["preferred_vendor_id"],
            ["vendors.id"],
            name=op.f("fk_products_preferred_vendor_id_vendors"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_products")),
        sa.UniqueConstraint("sku", name="uq_products_sku"),
    )
    op.create_index(op.f("ix_products_category_id"), "products", ["category_id"])
    op.create_index(
        op.f("ix_products_preferred_vendor_id"),
        "products",
        ["preferred_vendor_id"],
    )
    op.create_table(
        "inventory_counts",
        sa.Column("counted_by_id", sa.Uuid(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["counted_by_id"],
            ["users.id"],
            name=op.f("fk_inventory_counts_counted_by_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_inventory_counts")),
    )
    op.create_index(
        op.f("ix_inventory_counts_counted_by_id"),
        "inventory_counts",
        ["counted_by_id"],
    )
    op.create_table(
        "inventory_count_items",
        sa.Column("inventory_count_id", sa.Uuid(), nullable=False),
        sa.Column("product_id", sa.Uuid(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "quantity >= 0",
            name=op.f("ck_inventory_count_items_quantity_nonnegative"),
        ),
        sa.ForeignKeyConstraint(
            ["inventory_count_id"],
            ["inventory_counts.id"],
            name=op.f(
                "fk_inventory_count_items_inventory_count_id_inventory_counts"
            ),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name=op.f("fk_inventory_count_items_product_id_products"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_inventory_count_items")),
        sa.UniqueConstraint(
            "inventory_count_id",
            "product_id",
            name="uq_inventory_count_items_count_product",
        ),
    )
    op.create_index(
        op.f("ix_inventory_count_items_inventory_count_id"),
        "inventory_count_items",
        ["inventory_count_id"],
    )
    op.create_index(
        op.f("ix_inventory_count_items_product_id"),
        "inventory_count_items",
        ["product_id"],
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_inventory_count_items_product_id"),
        table_name="inventory_count_items",
    )
    op.drop_index(
        op.f("ix_inventory_count_items_inventory_count_id"),
        table_name="inventory_count_items",
    )
    op.drop_table("inventory_count_items")
    op.drop_index(
        op.f("ix_inventory_counts_counted_by_id"),
        table_name="inventory_counts",
    )
    op.drop_table("inventory_counts")
    op.drop_index(
        op.f("ix_products_preferred_vendor_id"),
        table_name="products",
    )
    op.drop_index(op.f("ix_products_category_id"), table_name="products")
    op.drop_table("products")
    op.drop_table("vendors")
    op.drop_table("categories")
    op.drop_table("users")
    sa.Enum(name="user_role").drop(op.get_bind(), checkfirst=False)
