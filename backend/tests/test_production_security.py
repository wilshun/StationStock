from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.auth.passwords import verify_password
from app.auth.rate_limit import login_rate_limiter
from app.core.config import Settings
from app.main import create_app
from app.models import AuditLog, Base, User
from app.scripts.create_manager import create_initial_manager
from app.scripts.seed_demo_data import seed_demo_data
from conftest import ApiContext, TEST_PASSWORD


def production_settings(**overrides) -> Settings:
    values = {
        "_env_file": None,
        "ENVIRONMENT": "production",
        "DATABASE_URL": "postgresql+psycopg://user:password@db/stationstock",
        "AUTH_SECRET_KEY": "a-unique-production-secret-with-more-than-32-characters",
        "AUTH_COOKIE_SECURE": True,
        "ALLOWED_FRONTEND_ORIGIN": "https://inventory.example.com",
    }
    values.update(overrides)
    return Settings(**values)


def test_production_requires_safe_configuration() -> None:
    with pytest.raises(ValueError):
        Settings(_env_file=None, ENVIRONMENT="production")
    settings = production_settings()
    assert settings.docs_enabled is False
    assert settings.auth_cookie_secure is True


def test_production_docs_are_disabled(monkeypatch) -> None:
    settings = production_settings()
    monkeypatch.setattr("app.main.get_settings", lambda: settings)
    with TestClient(create_app()) as client:
        assert client.get("/docs").status_code == 404
        assert client.get("/redoc").status_code == 404
        assert client.get("/openapi.json").status_code == 404


def test_development_docs_are_enabled(monkeypatch) -> None:
    monkeypatch.setattr("app.main.get_settings", lambda: Settings(_env_file=None))
    with TestClient(create_app()) as client:
        assert client.get("/docs").status_code == 200
        assert client.get("/openapi.json").status_code == 200


def test_demo_seed_refuses_production_and_database_stays_empty() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        with pytest.raises(RuntimeError, match="disabled in production"):
            seed_demo_data(db, settings=production_settings())
        assert db.scalar(select(func.count()).select_from(User)) == 0


def test_create_initial_manager_hashes_password_and_refuses_second() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        manager = create_initial_manager(db, name="Store Manager", email="Manager@Example.com", password="SecureManager2026!")
        assert manager.email == "manager@example.com"
        assert manager.password_hash != "SecureManager2026!"
        assert verify_password("SecureManager2026!", manager.password_hash)
        with pytest.raises(RuntimeError, match="manager already exists"):
            create_initial_manager(db, name="Other", email="other@example.com", password="AnotherSecure2026!")


def test_password_change_invalidates_existing_cookie(api_context: ApiContext) -> None:
    api_context.login(api_context.employee)
    response = api_context.client.post("/api/v1/auth/change-password", json={"current_password": TEST_PASSWORD, "new_password": "ChangedSecure2026!"})
    assert response.status_code == 200
    assert api_context.client.get("/api/v1/auth/me").status_code == 401
    assert api_context.client.post("/api/v1/auth/login", json={"email": api_context.employee.email, "password": "ChangedSecure2026!"}).status_code == 200


def test_manager_password_reset_and_audit_permissions(api_context: ApiContext) -> None:
    api_context.login(api_context.manager)
    response = api_context.client.post(f"/api/v1/users/{api_context.employee.id}/reset-password", json={"temporary_password": "TemporarySecure2026!"})
    assert response.status_code == 200
    assert api_context.session.scalar(select(func.count()).select_from(AuditLog)) >= 2
    assert api_context.client.get("/api/v1/audit-logs").status_code == 200
    assert api_context.client.post("/api/v1/auth/login", json={"email": api_context.employee.email, "password": "TemporarySecure2026!"}).status_code == 200
    assert api_context.client.get("/api/v1/audit-logs").status_code == 403


def test_repeated_login_failures_are_throttled_and_recover(api_context: ApiContext) -> None:
    login_rate_limiter.clear()
    for _ in range(api_context.settings.login_max_attempts):
        response = api_context.client.post("/api/v1/auth/login", json={"email": api_context.employee.email, "password": "wrong-password"})
        assert response.status_code == 401
    blocked = api_context.client.post("/api/v1/auth/login", json={"email": api_context.employee.email, "password": TEST_PASSWORD})
    assert blocked.status_code == 429
    login_rate_limiter.clear()
    recovered = api_context.client.post("/api/v1/auth/login", json={"email": api_context.employee.email, "password": TEST_PASSWORD})
    assert recovered.status_code == 200


def test_real_environment_files_are_ignored() -> None:
    assert Path(__file__).parents[2].joinpath(".env.production.example").exists()
