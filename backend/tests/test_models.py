from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import (
    Base,
    Category,
    InventoryCount,
    InventoryCountItem,
    Product,
    User,
    UserRole,
    Vendor,
)


@pytest.fixture
def db_session() -> Iterator[Session]:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


def test_core_schema_contains_only_expected_tables() -> None:
    assert set(Base.metadata.tables) == {
        "users",
        "categories",
        "vendors",
        "products",
        "inventory_counts",
        "inventory_count_items",
    }


def test_required_unique_constraints_are_present() -> None:
    expected_constraints = {
        "categories": "uq_categories_name",
        "vendors": "uq_vendors_name",
        "products": "uq_products_sku",
        "inventory_count_items": "uq_inventory_count_items_count_product",
    }

    for table_name, constraint_name in expected_constraints.items():
        constraint_names = {
            constraint.name for constraint in Base.metadata.tables[table_name].constraints
        }
        assert constraint_name in constraint_names


def test_user_email_is_normalized() -> None:
    user = User(
        email="  Manager@StationStock.Local  ",
        full_name="Store Manager",
        password_hash="test-password-hash",
    )

    assert user.email == "manager@stationstock.local"


def test_model_relationships_are_bidirectional() -> None:
    user = User(
        email="manager@example.com",
        full_name="Store Manager",
        password_hash="test-password-hash",
        role=UserRole.MANAGER,
    )
    category = Category(name="Beverages")
    vendor = Vendor(name="Preferred Supplier")
    product = Product(
        sku="BEV-001",
        name="Sparkling Water",
        category=category,
        preferred_vendor=vendor,
        minimum_quantity=2,
        target_quantity=12,
    )
    inventory_count = InventoryCount(started_by=user)
    item = InventoryCountItem(product=product, quantity=8)
    inventory_count.items.append(item)

    assert product in category.products
    assert product in vendor.preferred_products
    assert inventory_count in user.started_inventory_counts
    assert item.inventory_count is inventory_count
    assert item in product.inventory_count_items


@pytest.mark.parametrize(
    ("minimum_quantity", "target_quantity"),
    [(-1, 5), (5, 4)],
)
def test_product_rejects_invalid_quantity_thresholds(
    db_session: Session,
    minimum_quantity: int,
    target_quantity: int,
) -> None:
    category = Category(name="Snacks")
    invalid_product = Product(
        sku="SNK-001",
        name="Chips",
        category=category,
        minimum_quantity=minimum_quantity,
        target_quantity=target_quantity,
    )
    db_session.add(invalid_product)

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_inventory_count_item_rejects_negative_quantity(db_session: Session) -> None:
    user = User(
        email="employee@example.com",
        full_name="Store Employee",
        password_hash="test-password-hash",
    )
    category = Category(name="Household")
    product = Product(
        sku="HOU-001",
        name="Paper Towels",
        category=category,
        minimum_quantity=1,
        target_quantity=6,
    )
    inventory_count = InventoryCount(
        started_by=user,
        items=[InventoryCountItem(product=product, quantity=-1)],
    )
    db_session.add(inventory_count)

    with pytest.raises(IntegrityError):
        db_session.commit()


def test_inventory_count_rejects_duplicate_products(db_session: Session) -> None:
    user = User(
        email="employee@example.com",
        full_name="Store Employee",
        password_hash="test-password-hash",
    )
    category = Category(name="Household")
    product = Product(
        sku="HOU-001",
        name="Paper Towels",
        category=category,
        minimum_quantity=1,
        target_quantity=6,
    )
    inventory_count = InventoryCount(
        started_by=user,
        items=[
            InventoryCountItem(product=product, quantity=4),
            InventoryCountItem(product=product, quantity=5),
        ],
    )
    db_session.add(inventory_count)

    with pytest.raises(IntegrityError):
        db_session.commit()
