from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.auth.passwords import verify_password
from app.models import Base, User, UserRole
from app.scripts.seed_users import DEVELOPMENT_PASSWORD, seed_development_users


def test_seed_users_is_idempotent_and_passwords_verify() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        first_result = seed_development_users(session)
        first_hashes = {
            user.email: user.password_hash for user in session.scalars(select(User)).all()
        }
        second_result = seed_development_users(session)
        users = session.scalars(select(User).order_by(User.email)).all()

        assert first_result.created == (
            "manager@stationstock.local",
            "employee@stationstock.local",
        )
        assert not first_result.existing
        assert not second_result.created
        assert second_result.existing == (
            "manager@stationstock.local",
            "employee@stationstock.local",
        )
        assert session.scalar(select(func.count()).select_from(User)) == 2
        assert {user.role for user in users} == {UserRole.MANAGER, UserRole.EMPLOYEE}
        for user in users:
            assert user.password_hash == first_hashes[user.email]
            assert verify_password(DEVELOPMENT_PASSWORD, user.password_hash)

    engine.dispose()
