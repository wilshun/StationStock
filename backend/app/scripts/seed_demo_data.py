from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.service import get_user_by_email
from app.db.session import SessionLocal, get_engine
from app.models import (
    Category,
    InventoryCount,
    InventoryCountItem,
    Product,
    Vendor,
)
from app.scripts.seed_users import ensure_not_production, seed_development_users
from app.core.config import Settings
from app.services.inventory_counts import submit_inventory_count


@dataclass(frozen=True)
class DemoProduct:
    sku: str
    name: str
    category: str
    vendor: str
    minimum: int
    target: int
    unit: str


CATEGORY_NAMES = ("Energy Drinks", "Soda", "Water", "Chips", "Candy", "Snacks")
VENDOR_NAMES = (
    "Metro Beverage Supply",
    "Regional Snack Distribution",
    "Convenience Wholesale Partners",
)
DEMO_PRODUCTS = (
    DemoProduct("ENG-RED-12", "Red Bull Original 12 oz", "Energy Drinks", "Metro Beverage Supply", 8, 24, "12 oz can"),
    DemoProduct("ENG-MON-16", "Monster Energy Original 16 oz", "Energy Drinks", "Metro Beverage Supply", 8, 24, "16 oz can"),
    DemoProduct("ENG-CEL-12", "Celsius Sparkling Orange 12 oz", "Energy Drinks", "Metro Beverage Supply", 6, 18, "12 oz can"),
    DemoProduct("SOD-COK-20", "Coca-Cola 20 oz", "Soda", "Metro Beverage Supply", 12, 36, "20 oz bottle"),
    DemoProduct("SOD-DIE-20", "Diet Coke 20 oz", "Soda", "Metro Beverage Supply", 8, 24, "20 oz bottle"),
    DemoProduct("SOD-SPR-20", "Sprite 20 oz", "Soda", "Metro Beverage Supply", 8, 24, "20 oz bottle"),
    DemoProduct("WAT-DAS-20", "Dasani Water 20 oz", "Water", "Metro Beverage Supply", 12, 36, "20 oz bottle"),
    DemoProduct("WAT-SMA-1L", "smartwater 1 Liter", "Water", "Metro Beverage Supply", 6, 18, "1 liter bottle"),
    DemoProduct("WAT-ESS-1L", "Essentia Water 1 Liter", "Water", "Metro Beverage Supply", 4, 12, "1 liter bottle"),
    DemoProduct("CHP-LAY-REG", "Lay's Classic Chips", "Chips", "Regional Snack Distribution", 8, 24, "2.625 oz bag"),
    DemoProduct("CHP-DOR-NAC", "Doritos Nacho Cheese", "Chips", "Regional Snack Distribution", 8, 24, "2.75 oz bag"),
    DemoProduct("CHP-CHE-CRU", "Cheetos Crunchy", "Chips", "Regional Snack Distribution", 6, 18, "3.25 oz bag"),
    DemoProduct("CHP-FUN-ORI", "Funyuns Original", "Chips", "Regional Snack Distribution", 4, 12, "2.125 oz bag"),
    DemoProduct("CAN-SNI-REG", "Snickers Bar", "Candy", "Convenience Wholesale Partners", 12, 36, "1.86 oz bar"),
    DemoProduct("CAN-REE-CUP", "Reese's Peanut Butter Cups", "Candy", "Convenience Wholesale Partners", 12, 36, "1.5 oz pack"),
    DemoProduct("CAN-MMS-PEA", "M&M's Peanut", "Candy", "Convenience Wholesale Partners", 8, 24, "1.74 oz pack"),
    DemoProduct("CAN-SKI-ORI", "Skittles Original", "Candy", "Convenience Wholesale Partners", 8, 24, "2.17 oz pack"),
    DemoProduct("SNK-CLI-CHO", "CLIF Bar Chocolate Chip", "Snacks", "Convenience Wholesale Partners", 4, 12, "2.4 oz bar"),
    DemoProduct("SNK-POP-SEA", "Popcorn Sea Salt", "Snacks", "Regional Snack Distribution", 4, 12, "1 oz bag"),
    DemoProduct("SNK-TRM-BEE", "Beef Jerky Original", "Snacks", "Convenience Wholesale Partners", 4, 10, "2 oz bag"),
    DemoProduct("SNK-MIX-TRAIL", "Classic Trail Mix", "Snacks", "Convenience Wholesale Partners", 3, 9, "3 oz bag"),
)


@dataclass(frozen=True)
class DemoSeedResult:
    categories_created: int
    vendors_created: int
    products_created: int
    counts_created: int


def seed_demo_data(db: Session, *, settings: Settings | None = None) -> DemoSeedResult:
    seed_development_users(db, settings=settings)
    categories_created = 0
    vendors_created = 0
    products_created = 0
    counts_created = 0

    categories: dict[str, Category] = {}
    for name in CATEGORY_NAMES:
        category = db.scalar(select(Category).where(func.lower(Category.name) == name.lower()))
        if category is None:
            category = Category(name=name, description=f"Development demo {name.lower()}")
            db.add(category)
            db.flush()
            categories_created += 1
        categories[name] = category

    vendors: dict[str, Vendor] = {}
    for name in VENDOR_NAMES:
        vendor = db.scalar(select(Vendor).where(func.lower(Vendor.name) == name.lower()))
        if vendor is None:
            vendor = Vendor(name=name, notes="Development demo vendor")
            db.add(vendor)
            db.flush()
            vendors_created += 1
        vendors[name] = vendor

    products: dict[str, Product] = {}
    for definition in DEMO_PRODUCTS:
        product = db.scalar(
            select(Product).where(func.lower(Product.sku) == definition.sku.lower())
        )
        if product is None:
            product = Product(
                sku=definition.sku,
                name=definition.name,
                unit_description=definition.unit,
                category=categories[definition.category],
                preferred_vendor=vendors[definition.vendor],
                minimum_quantity=definition.minimum,
                target_quantity=definition.target,
            )
            db.add(product)
            db.flush()
            products_created += 1
        products[definition.sku] = product

    employee = get_user_by_email(db, "employee@stationstock.local")
    manager = get_user_by_email(db, "manager@stationstock.local")
    if employee is None or manager is None:
        raise RuntimeError("Development users were not created")

    count_specs = (
        (
            "StationStock Core demo count 1",
            employee,
            datetime.now(UTC) - timedelta(days=2),
            {
                definition.sku: max(definition.minimum + 3, definition.target - 2)
                for definition in DEMO_PRODUCTS[:10]
            },
        ),
        (
            "StationStock Core demo count 2",
            manager,
            datetime.now(UTC) - timedelta(days=1),
            {
                definition.sku: (
                    max(definition.minimum - 2, 0)
                    if index % 3 == 0
                    else definition.minimum + 2
                )
                for index, definition in enumerate(DEMO_PRODUCTS[:20])
            },
        ),
    )
    for notes, user, submitted_at, quantities in count_specs:
        existing = db.scalar(select(InventoryCount.id).where(InventoryCount.notes == notes))
        if existing is not None:
            continue
        inventory_count = InventoryCount(
            started_by=user,
            notes=notes,
            items=[
                InventoryCountItem(product=products[sku], quantity=quantity)
                for sku, quantity in quantities.items()
                if products[sku].is_active
            ],
        )
        db.add(inventory_count)
        db.flush()
        submit_inventory_count(inventory_count, user, submitted_at=submitted_at)
        counts_created += 1

    db.commit()
    return DemoSeedResult(
        categories_created=categories_created,
        vendors_created=vendors_created,
        products_created=products_created,
        counts_created=counts_created,
    )


def main() -> None:
    try:
        ensure_not_production()
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from None
    with SessionLocal(bind=get_engine()) as db:
        result = seed_demo_data(db)
    print(
        "Core demo seed complete: "
        f"{result.categories_created} categories, "
        f"{result.vendors_created} vendors, "
        f"{result.products_created} products, "
        f"{result.counts_created} counts created"
    )


if __name__ == "__main__":
    main()
