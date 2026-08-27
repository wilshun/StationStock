from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, Index, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.inventory_count import InventoryCount


class UserRole(StrEnum):
    MANAGER = "manager"
    EMPLOYEE = "employee"


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
        Index("uq_users_email_lower", text("lower(email)"), unique=True),
    )

    email: Mapped[str] = mapped_column(String(320), nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(
            UserRole,
            name="user_role",
            values_callable=lambda roles: [role.value for role in roles],
        ),
        nullable=False,
        default=UserRole.EMPLOYEE,
        server_default=UserRole.EMPLOYEE.value,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    inventory_counts: Mapped[list[InventoryCount]] = relationship(
        back_populates="counted_by"
    )

    @validates("email")
    def normalize_email(self, _key: str, email: str) -> str:
        return email.strip().lower()
