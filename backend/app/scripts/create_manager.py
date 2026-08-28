import argparse
import getpass
import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.passwords import hash_password, validate_password_strength
from app.auth.service import get_user_by_email
from app.db.session import SessionLocal, get_engine
from app.models import User, UserRole
from app.services.audit import record_audit


EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def create_initial_manager(db: Session, *, name: str, email: str, password: str) -> User:
    normalized_email = email.strip().lower()
    if not name.strip():
        raise ValueError("Name is required")
    if not EMAIL_PATTERN.fullmatch(normalized_email):
        raise ValueError("Invalid email address")
    validate_password_strength(password)
    if db.scalar(select(User.id).where(User.role == UserRole.MANAGER)) is not None:
        raise RuntimeError("A manager already exists; use the authenticated user-management API")
    if get_user_by_email(db, normalized_email) is not None:
        raise RuntimeError("An account with that email already exists")
    manager = User(email=normalized_email, full_name=name.strip(), password_hash=hash_password(password), role=UserRole.MANAGER)
    db.add(manager)
    db.flush()
    record_audit(db, "user.initial_manager_created", "user", actor_user_id=manager.id, target_id=manager.id)
    db.commit()
    db.refresh(manager)
    return manager


def main() -> None:
    parser = argparse.ArgumentParser(description="Create the first StationStock manager")
    parser.add_argument("--name", required=True)
    parser.add_argument("--email", required=True)
    args = parser.parse_args()
    password = getpass.getpass("Password: ")
    confirmation = getpass.getpass("Confirm password: ")
    if password != confirmation:
        raise SystemExit("Passwords do not match")
    with SessionLocal(bind=get_engine()) as db:
        manager = create_initial_manager(db, name=args.name, email=args.email, password=password)
    print(f"Created initial manager: {manager.email}")


if __name__ == "__main__":
    main()
