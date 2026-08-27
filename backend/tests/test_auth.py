from collections.abc import Iterator
from datetime import timedelta

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.auth.dependencies import require_manager
from app.auth.passwords import hash_password
from app.auth.tokens import create_access_token
from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.main import app
from app.models import Base, User, UserRole


TEST_PASSWORD = "StationStockDev!2026"


@pytest.fixture
def auth_context() -> Iterator[tuple[TestClient, Session, Settings]]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session = Session(engine)
    password_hash = hash_password(TEST_PASSWORD)
    session.add_all(
        [
            User(
                email="manager@stationstock.local",
                full_name="Development Manager",
                password_hash=password_hash,
                role=UserRole.MANAGER,
            ),
            User(
                email="employee@stationstock.local",
                full_name="Development Employee",
                password_hash=password_hash,
                role=UserRole.EMPLOYEE,
            ),
            User(
                email="inactive@stationstock.local",
                full_name="Inactive Employee",
                password_hash=password_hash,
                role=UserRole.EMPLOYEE,
                is_active=False,
            ),
        ]
    )
    session.commit()
    settings = Settings(
        _env_file=None,
        AUTH_SECRET_KEY="test-secret-that-is-not-used-outside-tests",
        ACCESS_TOKEN_EXPIRE_MINUTES=15,
        AUTH_COOKIE_NAME="stationstock_test_token",
        AUTH_COOKIE_SECURE=False,
        AUTH_COOKIE_SAMESITE="lax",
    )

    def override_get_db() -> Iterator[Session]:
        yield session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_settings] = lambda: settings

    with TestClient(app) as client:
        yield client, session, settings

    app.dependency_overrides.clear()
    session.close()
    engine.dispose()


def login(client: TestClient, email: str, password: str = TEST_PASSWORD):
    return client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )


@pytest.mark.parametrize(
    ("email", "role"),
    [
        ("manager@stationstock.local", "manager"),
        ("employee@stationstock.local", "employee"),
    ],
)
def test_active_users_can_log_in(
    auth_context: tuple[TestClient, Session, Settings],
    email: str,
    role: str,
) -> None:
    client, _session, settings = auth_context

    response = login(client, f"  {email.upper()}  ")

    assert response.status_code == 200
    assert response.json()["email"] == email
    assert response.json()["role"] == role
    assert "password_hash" not in response.json()
    assert settings.auth_cookie_name in response.cookies
    assert "HttpOnly" in response.headers["set-cookie"]


@pytest.mark.parametrize(
    ("email", "password"),
    [
        ("manager@stationstock.local", "incorrect-password"),
        ("unknown@stationstock.local", TEST_PASSWORD),
        ("inactive@stationstock.local", TEST_PASSWORD),
    ],
)
def test_login_rejects_invalid_credentials_consistently(
    auth_context: tuple[TestClient, Session, Settings],
    email: str,
    password: str,
) -> None:
    client, _session, _settings = auth_context

    response = login(client, email, password)

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid email or password"}


def test_current_user_returns_authenticated_user(
    auth_context: tuple[TestClient, Session, Settings],
) -> None:
    client, _session, _settings = auth_context
    assert login(client, "manager@stationstock.local").status_code == 200

    response = client.get("/api/v1/auth/me")

    assert response.status_code == 200
    assert response.json()["email"] == "manager@stationstock.local"
    assert response.json()["role"] == "manager"
    assert "password_hash" not in response.json()


def test_current_user_rejects_unauthenticated_request(
    auth_context: tuple[TestClient, Session, Settings],
) -> None:
    client, _session, _settings = auth_context

    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_current_user_rejects_tampered_token(
    auth_context: tuple[TestClient, Session, Settings],
) -> None:
    client, _session, settings = auth_context
    client.cookies.set(settings.auth_cookie_name, "not-a-valid-token", path="/api")

    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_current_user_rejects_expired_token(
    auth_context: tuple[TestClient, Session, Settings],
) -> None:
    client, session, settings = auth_context
    user = session.query(User).filter_by(email="manager@stationstock.local").one()
    token = create_access_token(
        user.id,
        settings=settings,
        expires_delta=timedelta(seconds=-1),
    )
    client.cookies.set(settings.auth_cookie_name, token, path="/api")

    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_inactive_user_is_rejected_even_with_valid_token(
    auth_context: tuple[TestClient, Session, Settings],
) -> None:
    client, session, settings = auth_context
    user = session.query(User).filter_by(email="inactive@stationstock.local").one()
    token = create_access_token(user.id, settings=settings)
    client.cookies.set(settings.auth_cookie_name, token, path="/api")

    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_logout_clears_authentication_cookie(
    auth_context: tuple[TestClient, Session, Settings],
) -> None:
    client, _session, settings = auth_context
    assert login(client, "manager@stationstock.local").status_code == 200

    response = client.post("/api/v1/auth/logout")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert settings.auth_cookie_name not in client.cookies
    assert "Max-Age=0" in response.headers["set-cookie"]


def test_manager_authorization_allows_manager_and_denies_employee(
    auth_context: tuple[TestClient, Session, Settings],
) -> None:
    _client, session, _settings = auth_context
    manager = session.query(User).filter_by(email="manager@stationstock.local").one()
    employee = session.query(User).filter_by(email="employee@stationstock.local").one()

    assert require_manager(manager) is manager
    with pytest.raises(HTTPException) as exc_info:
        require_manager(employee)
    assert exc_info.value.status_code == 403
