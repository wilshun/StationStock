"""add user authentication fields

Revision ID: 797a680c2300
Revises: a5bfce1c4424
Create Date: 2026-08-27 15:22:11.881411
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "797a680c2300"
down_revision: str | None = "a5bfce1c4424"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("password_hash", sa.String(length=255), nullable=True),
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM users WHERE password_hash IS NULL) THEN
                RAISE EXCEPTION
                    'Existing users require password hashes before authentication migration';
            END IF;
        END
        $$
        """
    )
    op.alter_column("users", "password_hash", nullable=False)
    op.execute("UPDATE users SET email = lower(btrim(email))")
    op.create_index(
        "uq_users_email_lower",
        "users",
        [sa.literal_column("lower(email)")],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_users_email_lower", table_name="users")
    op.drop_column("users", "password_hash")
