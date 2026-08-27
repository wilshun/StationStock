from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.inventory_count_item import InventoryCountItem
    from app.models.user import User


class InventoryCountStatus(StrEnum):
    DRAFT = "draft"
    SUBMITTED = "submitted"


class InventoryCount(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "inventory_counts"

    status: Mapped[InventoryCountStatus] = mapped_column(
        Enum(
            InventoryCountStatus,
            name="inventory_count_status",
            values_callable=lambda statuses: [status.value for status in statuses],
        ),
        nullable=False,
        default=InventoryCountStatus.DRAFT,
        server_default=InventoryCountStatus.DRAFT.value,
        index=True,
    )
    started_by_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    submitted_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    started_by: Mapped[User] = relationship(
        back_populates="started_inventory_counts",
        foreign_keys=[started_by_user_id],
    )
    submitted_by: Mapped[User | None] = relationship(
        back_populates="submitted_inventory_counts",
        foreign_keys=[submitted_by_user_id],
    )
    items: Mapped[list[InventoryCountItem]] = relationship(
        back_populates="inventory_count",
        cascade="all, delete-orphan",
    )
