from app.auth.passwords import verify_password
from app.models import User, UserRole
from conftest import ApiContext


def test_user_endpoints_require_manager(api_context: ApiContext) -> None:
    assert api_context.client.get("/api/v1/users").status_code == 401
    api_context.login(api_context.employee)
    assert api_context.client.get("/api/v1/users").status_code == 403
    assert (
        api_context.client.post(
            "/api/v1/users",
            json={
                "email": "blocked@stationstock.local",
                "full_name": "Blocked User",
                "password": "Password!123",
            },
        ).status_code
        == 403
    )


def test_manager_can_create_list_and_update_user(api_context: ApiContext) -> None:
    api_context.login(api_context.manager)
    response = api_context.client.post(
        "/api/v1/users",
        json={
            "email": "  New.User@StationStock.Local ",
            "full_name": "New User",
            "password": "SecurePassword!123",
            "role": "employee",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "new.user@stationstock.local"
    assert "password_hash" not in body
    user = api_context.session.query(User).filter_by(email=body["email"]).one()
    assert verify_password("SecurePassword!123", user.password_hash)

    listing = api_context.client.get("/api/v1/users?role=employee&search=new.user")
    assert listing.status_code == 200
    assert listing.json()["total"] == 1
    assert "password_hash" not in listing.text

    update = api_context.client.patch(
        f"/api/v1/users/{user.id}",
        json={"role": "manager", "is_active": False},
    )
    assert update.status_code == 200
    assert update.json()["role"] == "manager"
    assert update.json()["is_active"] is False


def test_duplicate_email_and_self_lockout_are_rejected(api_context: ApiContext) -> None:
    api_context.login(api_context.manager)
    duplicate = api_context.client.post(
        "/api/v1/users",
        json={
            "email": api_context.employee.email.upper(),
            "full_name": "Duplicate",
            "password": "SecurePassword!123",
        },
    )
    assert duplicate.status_code == 409

    lockout = api_context.client.patch(
        f"/api/v1/users/{api_context.manager.id}",
        json={"role": UserRole.EMPLOYEE.value},
    )
    assert lockout.status_code == 400
