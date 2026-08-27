import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.passwords import perform_dummy_password_check, verify_password
from app.models.user import User


def normalize_email(email: str) -> str:
    return email.strip().lower()


def get_user_by_email(db: Session, email: str) -> User | None:
    statement = select(User).where(func.lower(User.email) == normalize_email(email))
    return db.scalar(statement)


def get_user_by_id(db: Session, user_id: uuid.UUID) -> User | None:
    return db.get(User, user_id)


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if user is None:
        perform_dummy_password_check(password)
        return None

    if not verify_password(password, user.password_hash) or not user.is_active:
        return None
    return user
