from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.api.schemas.categories import CategorySummary
from app.api.schemas.dashboard import LowStockItem
from app.api.schemas.products import ProductResponse
from app.api.schemas.vendors import VendorSummary
from app.models import InventoryCount, InventoryCountItem, InventoryCountStatus, Product


def latest_inventory_subquery():
    ranked = (
        select(
            InventoryCountItem.product_id.label("product_id"),
            InventoryCountItem.quantity.label("quantity"),
            InventoryCount.submitted_at.label("submitted_at"),
            InventoryCount.id.label("count_id"),
            func.row_number()
            .over(
                partition_by=InventoryCountItem.product_id,
                order_by=(InventoryCount.submitted_at.desc(), InventoryCount.id.desc()),
            )
            .label("row_number"),
        )
        .join(
            InventoryCount,
            InventoryCount.id == InventoryCountItem.inventory_count_id,
        )
        .where(InventoryCount.status == InventoryCountStatus.SUBMITTED)
        .subquery("ranked_inventory")
    )
    return (
        select(
            ranked.c.product_id,
            ranked.c.quantity,
            ranked.c.submitted_at,
            ranked.c.count_id,
        )
        .where(ranked.c.row_number == 1)
        .subquery("latest_inventory")
    )


def inventory_values(
    product: Product,
    latest_quantity: int | None,
) -> tuple[bool | None, int | None]:
    if latest_quantity is None:
        return None, None
    return (
        latest_quantity < product.minimum_quantity,
        max(product.target_quantity - latest_quantity, 0),
    )


def product_response(
    product: Product,
    latest_quantity: int | None,
    latest_count_at,
) -> ProductResponse:
    is_low_stock, reorder_quantity = inventory_values(product, latest_quantity)
    return ProductResponse(
        id=product.id,
        sku=product.sku,
        name=product.name,
        description=product.description,
        unit_description=product.unit_description,
        minimum_quantity=product.minimum_quantity,
        target_quantity=product.target_quantity,
        is_active=product.is_active,
        category=CategorySummary.model_validate(product.category),
        preferred_vendor=(
            VendorSummary.model_validate(product.preferred_vendor)
            if product.preferred_vendor is not None
            else None
        ),
        latest_quantity=latest_quantity,
        latest_count_at=latest_count_at,
        is_counted=latest_quantity is not None,
        is_low_stock=is_low_stock,
        recommended_reorder_quantity=reorder_quantity,
        created_at=product.created_at,
        updated_at=product.updated_at,
    )


def low_stock_statement() -> tuple[Select, object]:
    latest = latest_inventory_subquery()
    statement = (
        select(Product, latest.c.quantity, latest.c.submitted_at)
        .join(latest, latest.c.product_id == Product.id)
        .where(
            Product.is_active.is_(True),
            latest.c.quantity < Product.minimum_quantity,
        )
        .order_by(
            (Product.target_quantity - latest.c.quantity).desc(),
            Product.sku.asc(),
            Product.id.asc(),
        )
    )
    return statement, latest


def low_stock_response(product: Product, quantity: int, submitted_at) -> LowStockItem:
    return LowStockItem(
        product_id=product.id,
        sku=product.sku,
        name=product.name,
        category=CategorySummary.model_validate(product.category),
        preferred_vendor=(
            VendorSummary.model_validate(product.preferred_vendor)
            if product.preferred_vendor is not None
            else None
        ),
        latest_quantity=quantity,
        latest_count_at=submitted_at,
        minimum_quantity=product.minimum_quantity,
        target_quantity=product.target_quantity,
        recommended_reorder_quantity=max(product.target_quantity - quantity, 0),
    )


def latest_inventory_for_product(db: Session, product_id):
    latest = latest_inventory_subquery()
    return db.execute(
        select(latest.c.quantity, latest.c.submitted_at, latest.c.count_id).where(
            latest.c.product_id == product_id
        )
    ).one_or_none()
