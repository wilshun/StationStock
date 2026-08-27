from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.auth.passwords import verify_password
from app.models import (
    Base,
    Category,
    InventoryCount,
    InventoryCountStatus,
    Product,
    User,
    Vendor,
)
from app.scripts.seed_demo_data import seed_demo_data
from app.scripts.seed_users import DEVELOPMENT_PASSWORD
from app.services.inventory import latest_inventory_subquery


def test_demo_seed_is_idempotent_and_produces_core_scenarios() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        first = seed_demo_data(session)
        second = seed_demo_data(session)

        assert first.categories_created == 6
        assert first.vendors_created == 3
        assert first.products_created == 21
        assert first.counts_created == 2
        assert second.categories_created == 0
        assert second.vendors_created == 0
        assert second.products_created == 0
        assert second.counts_created == 0
        assert session.scalar(select(func.count()).select_from(Category)) == 6
        assert session.scalar(select(func.count()).select_from(Vendor)) == 3
        assert session.scalar(select(func.count()).select_from(Product)) == 21
        assert (
            session.scalar(
                select(func.count())
                .select_from(InventoryCount)
                .where(InventoryCount.status == InventoryCountStatus.SUBMITTED)
            )
            == 2
        )

        latest = latest_inventory_subquery()
        counted = session.scalar(select(func.count()).select_from(latest))
        assert counted == 20
        low_stock = session.scalar(
            select(func.count())
            .select_from(Product)
            .join(latest, latest.c.product_id == Product.id)
            .where(latest.c.quantity < Product.minimum_quantity)
        )
        adequate = session.scalar(
            select(func.count())
            .select_from(Product)
            .join(latest, latest.c.product_id == Product.id)
            .where(latest.c.quantity >= Product.minimum_quantity)
        )
        assert low_stock and low_stock > 0
        assert adequate and adequate > 0

        users = session.scalars(select(User)).all()
        assert len(users) == 2
        assert all(
            verify_password(DEVELOPMENT_PASSWORD, user.password_hash) for user in users
        )

    engine.dispose()
