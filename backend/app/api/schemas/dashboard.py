import uuid
from datetime import datetime

from pydantic import BaseModel

from app.api.schemas.categories import CategorySummary
from app.api.schemas.inventory_counts import UserSummary
from app.api.schemas.vendors import VendorSummary


class LowStockItem(BaseModel):
    product_id: uuid.UUID
    sku: str
    name: str
    category: CategorySummary
    preferred_vendor: VendorSummary | None
    latest_quantity: int
    latest_count_at: datetime
    minimum_quantity: int
    target_quantity: int
    recommended_reorder_quantity: int


class RecentCountSummary(BaseModel):
    id: uuid.UUID
    submitted_at: datetime
    submitted_by: UserSummary
    item_count: int


class DashboardSummary(BaseModel):
    active_product_count: int
    low_stock_product_count: int
    uncounted_active_product_count: int
    active_category_count: int
    active_vendor_count: int
    total_submitted_count_sessions: int
    recent_submitted_count_sessions: list[RecentCountSummary]
    prioritized_low_stock: list[LowStockItem]
