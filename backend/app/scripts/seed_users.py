from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.auth.passwords import hash_password
from app.auth.service import get_user_by_email
from app.db.session import SessionLocal, get_engine
from app.models.user import User, UserRole


DEVELOPMENT_PASSWORD = "StationStockDev!2026"


@dataclass(frozen=True)
class DevelopmentUser:
    email: str
    full_name: str
    role: UserRole


DEVELOPMENT_USERS = (
    DevelopmentUser(
        email="manager@stationstock.local",
        full_name="Development Manager",
        role=UserRole.MANAGER,
    ),
    DevelopmentUser(
        email="employee@stationstock.local",
        full_name="Development Employee",
        role=UserRole.EMPLOYEE,
    ),
)


@dataclass(frozen=True)
class SeedResult:
    created: tuple[str, ...]
    existing: tuple[str, ...]


def seed_development_users(db: Session) -> SeedResult:
    created: list[str] = []
    existing: list[str] = []

    for user_data in DEVELOPMENT_USERS:
        email = user_data.email
        if get_user_by_email(db, email) is not None:
            existing.append(email)
            continue

        db.add(
            User(
                email=email,
                full_name=user_data.full_name,
                role=user_data.role,
                password_hash=hash_password(DEVELOPMENT_PASSWORD),
            )
        )
        created.append(email)

    db.commit()
    return SeedResult(created=tuple(created), existing=tuple(existing))


def main() -> None:
    with SessionLocal(bind=get_engine()) as db:
        result = seed_development_users(db)

    if result.created:
        print(f"Created development users: {', '.join(result.created)}")
    if result.existing:
        print(f"Kept existing users unchanged: {', '.join(result.existing)}")


if __name__ == "__main__":
    main()
