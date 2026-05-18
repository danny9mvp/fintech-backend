from datetime import datetime
from unittest.mock import MagicMock, patch

from fastapi import status


def _override_current_user(client, user_id=1):
    from app.api.deps import get_current_user
    from app.model.user import User

    client.app.dependency_overrides[get_current_user] = lambda: User(
        id=user_id, email="test@test.com", username="test", pwd_hash="xxx"
    )


def _make_mock_category(id=1, user_id=1, name="Default", budget=100.0, created_at=None):
    if created_at is None:
        created_at = datetime.now()
    c = MagicMock()
    c.id = id
    c.user_id = user_id
    c.name = name
    c.budget = budget
    c.created_at = created_at
    return c


def test_create_category(client):
    _override_current_user(client)

    mock_cat = _make_mock_category(id=1, name="Groceries", budget=500.0)

    with (
        patch("app.crud.movement_category.category_crud.create", return_value=mock_cat),
        patch("app.crud.movement.movement_crud.get_balance", return_value={"total_income": 1000.0, "total_expense": 0.0, "balance": 1000.0}),
        patch("app.crud.movement_category.category_crud.get_total_budgets", return_value=0.0),
    ):
        resp = client.post(
            "/categories/",
            json={"name": "Groceries", "budget": 500.0},
        )

    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.json()
    assert data["name"] == "Groceries"
    assert data["budget"] == 500.0
    assert "id" in data


def test_list_categories(client):
    _override_current_user(client)

    mock_cat = _make_mock_category(id=1, name="Rent", budget=1200.0)

    with patch("app.crud.movement_category.category_crud.get_by_user", return_value=[mock_cat]):
        resp = client.get("/categories/")

    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "Rent"


def test_get_category(client):
    _override_current_user(client)

    mock_cat = _make_mock_category(id=1, name="Salary")

    with patch("app.crud.movement_category.category_crud.get", return_value=mock_cat):
        resp = client.get("/categories/1")

    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["name"] == "Salary"


def test_update_category(client):
    _override_current_user(client)

    mock_cat = _make_mock_category(id=1, name="Old", budget=100.0)
    mock_updated = _make_mock_category(id=1, name="Updated", budget=200.0)

    with (
        patch("app.crud.movement_category.category_crud.get", return_value=mock_cat),
        patch("app.crud.movement_category.category_crud.update", return_value=mock_updated),
        patch("app.crud.movement.movement_crud.get_balance", return_value={"total_income": 1000.0, "total_expense": 0.0, "balance": 1000.0}),
        patch("app.crud.movement_category.category_crud.get_total_budgets", return_value=100.0),
    ):
        resp = client.patch(
            "/categories/1",
            json={"name": "Updated", "budget": 200.0},
        )

    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["name"] == "Updated"
    assert resp.json()["budget"] == 200.0


def test_delete_category(client):
    _override_current_user(client)

    mock_cat = _make_mock_category(id=1)

    with patch("app.crud.movement_category.category_crud.get", return_value=mock_cat), \
         patch("app.crud.movement_category.category_crud.remove"):
        resp = client.delete("/categories/1")

    assert resp.status_code == status.HTTP_204_NO_CONTENT


def test_category_ownership(client):
    _override_current_user(client, user_id=2)

    mock_cat = _make_mock_category(id=1, user_id=1)

    with patch("app.crud.movement_category.category_crud.get", return_value=mock_cat):
        resp = client.get("/categories/1")

    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_budget_summary(client):
    _override_current_user(client)

    cat1 = _make_mock_category(id=1, name="Food", budget=1000.0)
    cat2 = _make_mock_category(id=2, name="Rent", budget=None)

    with patch("app.crud.movement_category.category_crud.get_by_user", return_value=[cat1, cat2]), \
         patch("app.crud.movement.movement_crud.get_category_expense", side_effect=[200.0, 0.0]):
        resp = client.get("/categories/budget-summary")

    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert len(data) == 2
    assert data[0]["category_id"] == 1
    assert data[0]["category_name"] == "Food"
    assert data[0]["budget"] == 1000.0
    assert data[0]["total_expense"] == 200.0
    assert data[0]["usage_percentage"] == 20.0
    assert data[1]["usage_percentage"] is None
    assert data[1]["total_expense"] == 0.0
    assert "warning_level" not in data[0]
    assert "message" not in data[0]


def test_budget_warning_single(client):
    _override_current_user(client)

    mock_cat = _make_mock_category(id=1, name="Food", budget=1000.0)

    with patch("app.crud.movement_category.category_crud.get", return_value=mock_cat), \
         patch("app.crud.movement.movement_crud.get_category_expense", return_value=800.0):
        resp = client.get("/categories/1/check-budget")

    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["category_name"] == "Food"
    assert data["warning_level"] == "warning"
    assert data["usage_percentage"] == 80.0
    assert data["total_expense"] == 800.0
    assert data["budget"] == 1000.0


def test_budget_warning_single_not_found(client):
    _override_current_user(client)

    with patch("app.crud.movement_category.category_crud.get", return_value=None):
        resp = client.get("/categories/999/check-budget")

    assert resp.status_code == status.HTTP_404_NOT_FOUND


def _create_income_movement(client, auth_header, cat_id, amount=500.0):
    client.post(
        "/movements/",
        json={"type": "income", "amount": amount, "movement_category_id": cat_id},
        headers=auth_header,
    )


def test_create_category_budget_exceeds_balance(client, auth_header):
    cat_resp = client.post(
        "/categories/",
        json={"name": "SeedCat", "budget": 0},
        headers=auth_header,
    )
    seed_cat_id = cat_resp.json()["id"]
    _create_income_movement(client, auth_header, seed_cat_id, amount=100.0)
    resp = client.post(
        "/categories/",
        json={"name": "Expensive", "budget": 200.0},
        headers=auth_header,
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "exceed your balance" in resp.json()["detail"]


def test_create_category_budget_within_balance(client, auth_header):
    cat_resp = client.post(
        "/categories/",
        json={"name": "SeedCat", "budget": 0},
        headers=auth_header,
    )
    seed_cat_id = cat_resp.json()["id"]
    _create_income_movement(client, auth_header, seed_cat_id, amount=500.0)
    resp = client.post(
        "/categories/",
        json={"name": "Reasonable", "budget": 300.0},
        headers=auth_header,
    )
    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.json()["budget"] == 300.0


def test_create_category_no_budget(client, auth_header):
    resp = client.post(
        "/categories/",
        json={"name": "NoBudget"},
        headers=auth_header,
    )
    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.json()["budget"] is None


def test_create_category_total_budgets_exceed_balance(client, auth_header):
    cat_resp = client.post(
        "/categories/",
        json={"name": "SeedCat", "budget": 0},
        headers=auth_header,
    )
    seed_cat_id = cat_resp.json()["id"]
    _create_income_movement(client, auth_header, seed_cat_id, amount=500.0)
    client.post(
        "/categories/",
        json={"name": "First", "budget": 300.0},
        headers=auth_header,
    )
    resp = client.post(
        "/categories/",
        json={"name": "Second", "budget": 300.0},
        headers=auth_header,
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "exceed your balance" in resp.json()["detail"]


def test_update_category_budget_exceeds_balance(client, auth_header):
    seed_resp = client.post(
        "/categories/",
        json={"name": "IncomeCat", "budget": 0},
        headers=auth_header,
    )
    seed_cat_id = seed_resp.json()["id"]
    _create_income_movement(client, auth_header, seed_cat_id, amount=200.0)
    cat_resp = client.post(
        "/categories/",
        json={"name": "TestCat", "budget": 100.0},
        headers=auth_header,
    )
    cat_id = cat_resp.json()["id"]
    resp = client.patch(
        f"/categories/{cat_id}",
        json={"budget": 300.0},
        headers=auth_header,
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "exceed your balance" in resp.json()["detail"]


def test_update_category_budget_within_balance(client, auth_header):
    seed_resp = client.post(
        "/categories/",
        json={"name": "IncomeCat", "budget": 0},
        headers=auth_header,
    )
    seed_cat_id = seed_resp.json()["id"]
    _create_income_movement(client, auth_header, seed_cat_id, amount=200.0)
    cat_resp = client.post(
        "/categories/",
        json={"name": "TestCat", "budget": 100.0},
        headers=auth_header,
    )
    cat_id = cat_resp.json()["id"]
    resp = client.patch(
        f"/categories/{cat_id}",
        json={"budget": 150.0},
        headers=auth_header,
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["budget"] == 150.0



