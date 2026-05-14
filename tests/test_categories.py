from fastapi import status


def test_create_category(client, auth_header):
    resp = client.post(
        "/categories/",
        json={"name": "Groceries", "budget": 500.0},
        headers=auth_header,
    )
    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.json()
    assert data["name"] == "Groceries"
    assert data["budget"] == 500.0
    assert "id" in data


def test_list_categories(client, auth_header):
    client.post(
        "/categories/",
        json={"name": "Rent", "budget": 1200.0},
        headers=auth_header,
    )
    resp = client.get("/categories/", headers=auth_header)
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "Rent"


def test_get_category(client, auth_header):
    create = client.post(
        "/categories/",
        json={"name": "Salary"},
        headers=auth_header,
    )
    cat_id = create.json()["id"]
    resp = client.get(f"/categories/{cat_id}", headers=auth_header)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["name"] == "Salary"


def test_update_category(client, auth_header):
    create = client.post(
        "/categories/",
        json={"name": "Old", "budget": 100.0},
        headers=auth_header,
    )
    cat_id = create.json()["id"]
    resp = client.patch(
        f"/categories/{cat_id}",
        json={"name": "Updated", "budget": 200.0},
        headers=auth_header,
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["name"] == "Updated"
    assert resp.json()["budget"] == 200.0


def test_delete_category(client, auth_header):
    create = client.post(
        "/categories/",
        json={"name": "Temp"},
        headers=auth_header,
    )
    cat_id = create.json()["id"]
    resp = client.delete(f"/categories/{cat_id}", headers=auth_header)
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    get_resp = client.get(f"/categories/{cat_id}", headers=auth_header)
    assert get_resp.status_code == status.HTTP_404_NOT_FOUND


def test_category_ownership(client, auth_header):
    create = client.post(
        "/categories/",
        json={"name": "Mine"},
        headers=auth_header,
    )
    cat_id = create.json()["id"]

    client.post(
        "/auth/register",
        json={
            "email": "other@example.com",
            "password": "secret",
            "username": "other",
        },
    )
    resp2 = client.post(
        "/auth/login",
        json={"email": "other@example.com", "password": "secret"},
    )
    other_token = resp2.json()["access_token"]
    other_header = {"Authorization": f"Bearer {other_token}"}

    resp = client.get(f"/categories/{cat_id}", headers=other_header)
    assert resp.status_code == status.HTTP_404_NOT_FOUND
