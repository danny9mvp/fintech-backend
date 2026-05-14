from fastapi import status


def _create_category(client, auth_header, name="Default", budget=100.0):
    resp = client.post(
        "/categories/",
        json={"name": name, "budget": budget},
        headers=auth_header,
    )
    return resp.json()["id"]


def test_create_movement(client, auth_header):
    cat_id = _create_category(client, auth_header)
    resp = client.post(
        "/movements/",
        json={
            "type": "expense",
            "amount": 50.0,
            "description": "Lunch",
            "movement_category_id": cat_id,
        },
        headers=auth_header,
    )
    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.json()
    assert data["type"] == "expense"
    assert data["amount"] == 50.0
    assert data["description"] == "Lunch"
    assert data["movement_category_id"] == cat_id


def test_list_movements(client, auth_header):
    cat_id = _create_category(client, auth_header)
    client.post(
        "/movements/",
        json={
            "type": "income",
            "amount": 1000.0,
            "movement_category_id": cat_id,
        },
        headers=auth_header,
    )
    resp = client.get("/movements/", headers=auth_header)
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.json()) == 1


def test_get_movement(client, auth_header):
    cat_id = _create_category(client, auth_header)
    create = client.post(
        "/movements/",
        json={
            "type": "expense",
            "amount": 25.0,
            "movement_category_id": cat_id,
        },
        headers=auth_header,
    )
    mov_id = create.json()["id"]
    resp = client.get(f"/movements/{mov_id}", headers=auth_header)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["amount"] == 25.0


def test_update_movement(client, auth_header):
    cat_id = _create_category(client, auth_header)
    create = client.post(
        "/movements/",
        json={
            "type": "expense",
            "amount": 10.0,
            "movement_category_id": cat_id,
        },
        headers=auth_header,
    )
    mov_id = create.json()["id"]
    resp = client.patch(
        f"/movements/{mov_id}",
        json={"amount": 20.0},
        headers=auth_header,
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["amount"] == 20.0


def test_delete_movement(client, auth_header):
    cat_id = _create_category(client, auth_header)
    create = client.post(
        "/movements/",
        json={
            "type": "expense",
            "amount": 5.0,
            "movement_category_id": cat_id,
        },
        headers=auth_header,
    )
    mov_id = create.json()["id"]
    resp = client.delete(f"/movements/{mov_id}", headers=auth_header)
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    get_resp = client.get(f"/movements/{mov_id}", headers=auth_header)
    assert get_resp.status_code == status.HTTP_404_NOT_FOUND


def test_movement_invalid_category(client, auth_header):
    resp = client.post(
        "/movements/",
        json={
            "type": "expense",
            "amount": 50.0,
            "movement_category_id": 999,
        },
        headers=auth_header,
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_movement_ownership(client, auth_header):
    cat_id = _create_category(client, auth_header)
    create = client.post(
        "/movements/",
        json={
            "type": "expense",
            "amount": 30.0,
            "movement_category_id": cat_id,
        },
        headers=auth_header,
    )
    mov_id = create.json()["id"]

    client.post(
        "/auth/register",
        json={
            "email": "other2@example.com",
            "password": "secret",
            "username": "other2",
        },
    )
    resp2 = client.post(
        "/auth/login",
        json={"email": "other2@example.com", "password": "secret"},
    )
    other_header = {"Authorization": f"Bearer {resp2.json()['access_token']}"}

    resp = client.get(f"/movements/{mov_id}", headers=other_header)
    assert resp.status_code == status.HTTP_404_NOT_FOUND
