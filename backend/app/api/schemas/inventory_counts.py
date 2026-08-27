import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.api.schemas.products import ProductSummary
from app.models.inventory_count import InventoryCountStatus
from app.models.user import UserRole


class UserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    full_name: str
    role: UserRole


class InventoryCountCreate(BaseModel):
    notes: str | None = None


class InventoryCountUpdate(BaseModel):
    notes: str | None = None


class InventoryCountItemUpsert(BaseModel):
    quantity: int = Field(ge=0)
    notes: str | None = None


class InventoryCountItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    product: ProductSummary
    quantity: int
    notes: str | None
    created_at: datetime
    updated_at: datetime


class InventoryCountResponse(BaseModel):
    id: uuid.UUID
    status: InventoryCountStatus
    started_by: UserSummary
    submitted_by: UserSummary | None
    notes: str | None
    submitted_at: datetime | None
    created_at: datetime
    updated_at: datetime
    items: list[InventoryCountItemResponse]


class InventoryCountListItem(BaseModel):
    id: uuid.UUID
    status: InventoryCountStatus
    started_by: UserSummary
    submitted_by: UserSummary | None
    notes: str | None
    submitted_at: datetime | None
    created_at: datetime
    updated_at: datetime
    item_count: int
