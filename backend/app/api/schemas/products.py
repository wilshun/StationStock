import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.api.schemas.categories import CategorySummary
from app.api.schemas.vendors import VendorSummary


class ProductCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    unit_description: str | None = Field(default=None, max_length=100)
    category_id: uuid.UUID
    preferred_vendor_id: uuid.UUID | None = None
    minimum_quantity: int = Field(default=0, ge=0)
    target_quantity: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def validate_thresholds(self) -> "ProductCreate":
        if self.target_quantity < self.minimum_quantity:
            raise ValueError("target_quantity must be at least minimum_quantity")
        self.sku = self.sku.strip().upper()
        self.name = self.name.strip()
        return self


class ProductUpdate(BaseModel):
    sku: str | None = Field(default=None, min_length=1, max_length=100)
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    unit_description: str | None = Field(default=None, max_length=100)
    category_id: uuid.UUID | None = None
    preferred_vendor_id: uuid.UUID | None = None
    minimum_quantity: int | None = Field(default=None, ge=0)
    target_quantity: int | None = Field(default=None, ge=0)
    is_active: bool | None = None

    @model_validator(mode="after")
    def normalize_strings(self) -> "ProductUpdate":
        if self.sku is not None:
            self.sku = self.sku.strip().upper()
        if self.name is not None:
            self.name = self.name.strip()
        return self


class ProductResponse(BaseModel):
    id: uuid.UUID
    sku: str
    name: str
    description: str | None
    unit_description: str | None
    minimum_quantity: int
    target_quantity: int
    is_active: bool
    category: CategorySummary
    preferred_vendor: VendorSummary | None
    latest_quantity: int | None
    latest_count_at: datetime | None
    is_counted: bool
    is_low_stock: bool | None
    recommended_reorder_quantity: int | None
    created_at: datetime
    updated_at: datetime


class ProductCountHistoryItem(BaseModel):
    count_id: uuid.UUID
    submitted_at: datetime
    quantity: int
    submitted_by_user_id: uuid.UUID
    submitted_by_email: str


class ProductSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    sku: str
    name: str
