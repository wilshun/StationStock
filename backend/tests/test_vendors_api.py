from conftest import ApiContext


def test_vendor_permissions_crud_search_and_conflicts(api_context: ApiContext) -> None:
    api_context.login(api_context.employee)
    assert api_context.client.get("/api/v1/vendors").status_code == 200
    assert (
        api_context.client.post("/api/v1/vendors", json={"name": "Acme"}).status_code
        == 403
    )

    api_context.login(api_context.manager)
    created = api_context.client.post(
        "/api/v1/vendors",
        json={
            "name": " Acme Distribution ",
            "contact_name": "Alex Vendor",
            "phone": "555-0100",
            "email": "orders@acme.example",
            "notes": "Weekly delivery",
        },
    )
    assert created.status_code == 201
    vendor_id = created.json()["id"]
    assert created.json()["contact_name"] == "Alex Vendor"

    assert (
        api_context.client.post(
            "/api/v1/vendors", json={"name": "acme distribution"}
        ).status_code
        == 409
    )
    updated = api_context.client.patch(
        f"/api/v1/vendors/{vendor_id}",
        json={"phone": "555-0199", "is_active": False},
    )
    assert updated.status_code == 200
    assert updated.json()["phone"] == "555-0199"
    assert updated.json()["is_active"] is False

    listing = api_context.client.get("/api/v1/vendors?search=distribution&is_active=false")
    assert listing.status_code == 200
    assert listing.json()["total"] == 1
