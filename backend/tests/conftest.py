from collections.abc import Iterator
from dataclasses import dataclass

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.auth.passwords import hash_password
from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.main import app
from app.models import Base, User, UserRole


TEST_PASSWORD = "StationStockTest!2026"


@dataclass
class ApiContext:
    client: TestClient
    session: Session
    settings: Settings
    manager: User
    employee: User

    def login(self, user: User) -> None:
        response = self.client.post(
            "/api/v1/auth/login",
            json={"email": user.email, "password": TEST_PASSWORD},
        )
        assert response.status_code == 200


@pytest.fixture
def api_context() -> Iterator[ApiContext]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session = Session(engine)
    password_hash = hash_password(TEST_PASSWORD)
    manager = User(
        email="manager-api@stationstock.local",
        full_name="API Manager",
        password_hash=password_hash,
        role=UserRole.MANAGER,
    )
    employee = User(
        email="employee-api@stationstock.local",
        full_name="API Employee",
        password_hash=password_hash,
        role=UserRole.EMPLOYEE,
    )
    session.add_all([manager, employee])
    session.commit()
    settings = Settings(
        _env_file=None,
        AUTH_SECRET_KEY="core-api-test-secret-not-for-production",
        AUTH_COOKIE_NAME="stationstock_core_test_token",
        AUTH_COOKIE_SECURE=False,
    )

    def override_get_db() -> Iterator[Session]:
        yield session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_settings] = lambda: settings
    with TestClient(app) as client:
        yield ApiContext(client, session, settings, manager, employee)

    app.dependency_overrides.clear()
    session.close()
    engine.dispose()
