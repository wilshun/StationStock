import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.user import UserRole


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=1024)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, email: str) -> str:
        normalized = email.strip().lower()
        local_part, separator, domain = normalized.partition("@")
        if not separator or not local_part or not domain:
            raise ValueError("Invalid email address")
        return normalized


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime


class LogoutResponse(BaseModel):
    status: str
