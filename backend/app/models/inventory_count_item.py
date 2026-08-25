from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.inventory_count import InventoryCount
    from app.models.product import Product


class InventoryCountItem(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "inventory_count_items"
    __table_args__ = (
        CheckConstraint("quantity >= 0", name="quantity_nonnegative"),
        UniqueConstraint(
            "inventory_count_id",
            "product_id",
            name="uq_inventory_count_items_count_product",
        ),
    )

    inventory_count_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("inventory_counts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    inventory_count: Mapped[InventoryCount] = relationship(back_populates="items")
    product: Mapped[Product] = relationship(back_populates="inventory_count_items")
