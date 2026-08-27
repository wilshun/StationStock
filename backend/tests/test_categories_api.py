from conftest import ApiContext


def test_category_permissions_crud_and_duplicate_handling(api_context: ApiContext) -> None:
    api_context.login(api_context.employee)
    assert api_context.client.get("/api/v1/categories").status_code == 200
    assert (
        api_context.client.post("/api/v1/categories", json={"name": "Soda"}).status_code
        == 403
    )

    api_context.login(api_context.manager)
    created = api_context.client.post(
        "/api/v1/categories",
        json={"name": " Soda ", "description": "Carbonated drinks"},
    )
    assert created.status_code == 201
    category_id = created.json()["id"]

    duplicate = api_context.client.post(
        "/api/v1/categories",
        json={"name": "sOdA"},
    )
    assert duplicate.status_code == 409

    updated = api_context.client.patch(
        f"/api/v1/categories/{category_id}",
        json={"description": "Soft drinks", "is_active": False},
    )
    assert updated.status_code == 200
    assert updated.json()["is_active"] is False

    listing = api_context.client.get(
        "/api/v1/categories?search=od&page=1&page_size=1&is_active=false"
    )
    assert listing.status_code == 200
    assert listing.json()["total"] == 1
    assert listing.json()["pages"] == 1
    assert api_context.client.get("/api/v1/categories?page=0").status_code == 422
