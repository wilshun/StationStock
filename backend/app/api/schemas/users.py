import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.auth.service import normalize_email
from app.models.user import UserRole


class UserAdminResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserCreate(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    full_name: str = Field(min_length=1, max_length=200)
    password: str = Field(min_length=8, max_length=1024)
    role: UserRole = UserRole.EMPLOYEE
    is_active: bool = True

    @field_validator("email")
    @classmethod
    def normalize_user_email(cls, email: str) -> str:
        normalized = normalize_email(email)
        if "@" not in normalized:
            raise ValueError("Invalid email address")
        return normalized

    @field_validator("full_name")
    @classmethod
    def strip_full_name(cls, full_name: str) -> str:
        return full_name.strip()


class UserUpdate(BaseModel):
    role: UserRole | None = None
    is_active: bool | None = None
    password: str | None = Field(default=None, min_length=8, max_length=1024)
