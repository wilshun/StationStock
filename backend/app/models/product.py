from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Integer,
    Index,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.inventory_count_item import InventoryCountItem
    from app.models.vendor import Vendor


class Product(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("sku", name="uq_products_sku"),
        Index("uq_products_sku_lower", text("lower(sku)"), unique=True),
        CheckConstraint("minimum_quantity >= 0", name="minimum_quantity_nonnegative"),
        CheckConstraint(
            "target_quantity >= minimum_quantity",
            name="target_quantity_at_least_minimum",
        ),
    )

    sku: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    unit_description: Mapped[str | None] = mapped_column(String(100), nullable=True)
    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    preferred_vendor_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("vendors.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    minimum_quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )
    target_quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        index=True,
    )

    category: Mapped[Category] = relationship(back_populates="products")
    preferred_vendor: Mapped[Vendor | None] = relationship(back_populates="preferred_products")
    inventory_count_items: Mapped[list[InventoryCountItem]] = relationship(
        back_populates="product"
    )

    @validates("sku")
    def normalize_sku(self, _key: str, sku: str) -> str:
        return sku.strip().upper()

    @validates("name")
    def normalize_name(self, _key: str, name: str) -> str:
        return name.strip()
