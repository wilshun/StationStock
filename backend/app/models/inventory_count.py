from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.inventory_count_item import InventoryCountItem
    from app.models.user import User


class InventoryCount(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "inventory_counts"

    counted_by_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    counted_by: Mapped[User] = relationship(back_populates="inventory_counts")
    items: Mapped[list[InventoryCountItem]] = relationship(
        back_populates="inventory_count",
        cascade="all, delete-orphan",
    )
