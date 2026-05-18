from datetime import datetime
from unittest.mock import MagicMock, patch

from fastapi import status


def _create_category(client, auth_header, name="Default", budget=0):
    resp = client.post(
        "/categories/",
        json={"name": name, "budget": budget},
        headers=auth_header,
    )
    return resp.json()["id"]


def _create_income(client, auth_header, cat_id, amount=200.0):
    client.post(
        "/movements/",
        json={
            "type": "income",
            "amount": amount,
            "movement_category_id": cat_id,
        },
        headers=auth_header,
    )


def test_create_movement(client, auth_header):
    cat_id = _create_category(client, auth_header)
    _create_income(client, auth_header, cat_id)
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
    assert data["type"] == "EXPENSE"
    assert data["amount"] == 50.0
    assert data["description"] == "Lunch"
    assert data["movement_category_id"] == cat_id
    assert data["category_name"] == "Default"


def test_create_expense_insufficient_balance(client, auth_header):
    cat_id = _create_category(client, auth_header)
    resp = client.post(
        "/movements/",
        json={
            "type": "expense",
            "amount": 50.0,
            "movement_category_id": cat_id,
        },
        headers=auth_header,
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "Insufficient balance" in resp.json()["detail"]


def test_create_expense_with_sufficient_balance(client, auth_header):
    cat_id = _create_category(client, auth_header)
    client.post(
        "/movements/",
        json={
            "type": "income",
            "amount": 100.0,
            "movement_category_id": cat_id,
        },
        headers=auth_header,
    )
    resp = client.post(
        "/movements/",
        json={
            "type": "expense",
            "amount": 50.0,
            "movement_category_id": cat_id,
        },
        headers=auth_header,
    )
    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.json()["amount"] == 50.0


def test_create_expense_exact_balance(client, auth_header):
    cat_id = _create_category(client, auth_header)
    client.post(
        "/movements/",
        json={
            "type": "income",
            "amount": 100.0,
            "movement_category_id": cat_id,
        },
        headers=auth_header,
    )
    resp = client.post(
        "/movements/",
        json={
            "type": "expense",
            "amount": 100.0,
            "movement_category_id": cat_id,
        },
        headers=auth_header,
    )
    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.json()["amount"] == 100.0


def test_list_movements(client):
    from app.api.deps import get_current_user
    from app.model.user import User

    client.app.dependency_overrides[get_current_user] = lambda: User(
        id=1, email="test@test.com", username="test", pwd_hash="xxx"
    )

    now = datetime.now()
    mock_mov = MagicMock()
    mock_mov.id = 1
    mock_mov.user_id = 1
    mock_mov.movement_category_id = 1
    mock_mov.type = "income"
    mock_mov.amount = 1000.0
    mock_mov.description = None
    mock_mov.created_at = now
    mock_mov.category_name = "Default"

    with patch("app.crud.movement.movement_crud.count_user_movements", return_value=1), \
         patch("app.crud.movement.movement_crud.get_by_user", return_value=[mock_mov]):
        resp = client.get("/movements/")

    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["type"] == "income"
    assert data["items"][0]["amount"] == 1000.0
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert data["total_pages"] == 1
    assert data["has_next"] is False
    assert data["has_prev"] is False


def test_list_movements_pagination(client):
    from app.api.deps import get_current_user
    from app.model.user import User

    client.app.dependency_overrides[get_current_user] = lambda: User(
        id=1, email="test@test.com", username="test", pwd_hash="xxx"
    )

    now = datetime.now()
    mock_movements = []
    for i in range(6):
        m = MagicMock()
        m.id = i + 1
        m.user_id = 1
        m.movement_category_id = 1
        m.type = "expense"
        m.amount = float(i + 1)
        m.description = None
        m.created_at = now
        m.category_name = "Default"
        mock_movements.append(m)

    page_size = 5

    with patch("app.crud.movement.movement_crud.count_user_movements", return_value=6), \
         patch("app.crud.movement.movement_crud.get_by_user", return_value=mock_movements[:5]):
        page1 = client.get(f"/movements/?page=1&page_size={page_size}")
        assert page1.status_code == status.HTTP_200_OK
        d1 = page1.json()
        assert d1["total"] == 6
        assert len(d1["items"]) == 5
        assert d1["page"] == 1
        assert d1["page_size"] == page_size
        assert d1["total_pages"] == 2
        assert d1["has_next"] is True
        assert d1["has_prev"] is False

    with patch("app.crud.movement.movement_crud.count_user_movements", return_value=6), \
         patch("app.crud.movement.movement_crud.get_by_user", return_value=mock_movements[5:]):
        page2 = client.get(f"/movements/?page=2&page_size={page_size}")
        assert page2.status_code == status.HTTP_200_OK
        d2 = page2.json()
        assert d2["total"] == 6
        assert len(d2["items"]) == 1
        assert d2["page"] == 2
        assert d2["page_size"] == page_size
        assert d2["total_pages"] == 2
        assert d2["has_next"] is False
        assert d2["has_prev"] is True


def _override_current_user_mock(client, user_id=1):
    from app.api.deps import get_current_user
    from app.model.user import User

    client.app.dependency_overrides[get_current_user] = lambda: User(
        id=user_id, email="test@test.com", username="test", pwd_hash="xxx"
    )


def _make_mock_movement(id=1, type="expense", amount=50.0, description=None, category_id=1, category_name="Default", created_at=None):
    if created_at is None:
        created_at = datetime.now()
    m = MagicMock()
    m.id = id
    m.movement_category_id = category_id
    m.type = type
    m.amount = amount
    m.description = description
    m.created_at = created_at
    m.category_name = category_name
    return m


def test_list_movements_filter_by_type(client):
    _override_current_user_mock(client)

    mock_mov = _make_mock_movement(type="expense")

    with patch("app.crud.movement.movement_crud.count_user_movements", return_value=1), \
         patch("app.crud.movement.movement_crud.get_by_user", return_value=[mock_mov]):
        resp = client.get("/movements/?type=expense")

    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["type"] == "expense"


def test_list_movements_filter_by_category(client):
    _override_current_user_mock(client)

    mock_mov = _make_mock_movement(category_id=5, category_name="Bills")

    with patch("app.crud.movement.movement_crud.count_user_movements", return_value=1), \
         patch("app.crud.movement.movement_crud.get_by_user", return_value=[mock_mov]):
        resp = client.get("/movements/?category_id=5")

    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["movement_category_id"] == 5
    assert data["items"][0]["category_name"] == "Bills"


def test_list_movements_filter_by_date_range(client):
    _override_current_user_mock(client)

    mock_mov = _make_mock_movement()

    with patch("app.crud.movement.movement_crud.count_user_movements", return_value=1), \
         patch("app.crud.movement.movement_crud.get_by_user", return_value=[mock_mov]):
        resp = client.get("/movements/?date_from=2024-01-01&date_to=2024-12-31")

    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["total"] == 1


def test_list_movements_filter_no_results(client):
    _override_current_user_mock(client)

    with patch("app.crud.movement.movement_crud.count_user_movements", return_value=0):
        resp = client.get("/movements/?type=income&category_id=999")

    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["total"] == 0
    assert data["items"] == []
    assert data["total_pages"] == 0


def test_list_movements_category_name_in_response(client, auth_header):
    cat_id = _create_category(client, auth_header, name="Groceries")
    _create_income(client, auth_header, cat_id)
    create = client.post(
        "/movements/",
        json={"type": "expense", "amount": 30.0, "movement_category_id": cat_id},
        headers=auth_header,
    )
    mov_id = create.json()["id"]
    assert create.json()["category_name"] == "Groceries"

    resp = client.get("/movements/", headers=auth_header)
    assert resp.status_code == status.HTTP_200_OK
    item = next(i for i in resp.json()["items"] if i["id"] == mov_id)
    assert item["category_name"] == "Groceries"


def test_get_movement(client, auth_header):
    cat_id = _create_category(client, auth_header)
    _create_income(client, auth_header, cat_id)
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
    _create_income(client, auth_header, cat_id)
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
    _create_income(client, auth_header, cat_id)
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


def test_get_balance_returns_zero_when_no_movements(client):
    _override_current_user_mock(client)
    with patch("app.crud.movement.movement_crud.get_balance", return_value={
        "total_income": 0.0, "total_expense": 0.0, "balance": 0.0,
    }):
        resp = client.get("/movements/balance")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["total_income"] == 0.0
    assert data["total_expense"] == 0.0
    assert data["balance"] == 0.0


def test_get_balance_returns_correct_totals(client):
    _override_current_user_mock(client)
    with patch("app.crud.movement.movement_crud.get_balance", return_value={
        "total_income": 700.0, "total_expense": 150.0, "balance": 550.0,
    }):
        resp = client.get("/movements/balance")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["total_income"] == 700.0
    assert data["total_expense"] == 150.0
    assert data["balance"] == 550.0


def test_get_balance_returns_only_income(client):
    _override_current_user_mock(client)
    with patch("app.crud.movement.movement_crud.get_balance", return_value={
        "total_income": 1000.0, "total_expense": 0.0, "balance": 1000.0,
    }):
        resp = client.get("/movements/balance")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["total_income"] == 1000.0
    assert data["total_expense"] == 0.0
    assert data["balance"] == 1000.0


def test_get_balance_returns_negative_when_expenses_exceed_income(client):
    _override_current_user_mock(client)
    with patch("app.crud.movement.movement_crud.get_balance", return_value={
        "total_income": 0.0, "total_expense": 300.0, "balance": -300.0,
    }):
        resp = client.get("/movements/balance")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["total_income"] == 0.0
    assert data["total_expense"] == 300.0
    assert data["balance"] == -300.0


def test_get_balance_unauthorized(client):
    resp = client.get("/movements/balance")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_balance_scoped_to_user(client, auth_header):
    cat_id = _create_category(client, auth_header)
    client.post(
        "/movements/",
        json={"type": "income", "amount": 999.0, "movement_category_id": cat_id},
        headers=auth_header,
    )
    client.post(
        "/auth/register",
        json={"email": "other@test.com", "password": "secret", "username": "other"},
    )
    login = client.post(
        "/auth/login",
        json={"email": "other@test.com", "password": "secret"},
    )
    other_header = {"Authorization": f"Bearer {login.json()['access_token']}"}

    resp = client.get("/movements/balance", headers=other_header)
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["total_income"] == 0.0
    assert data["total_expense"] == 0.0
    assert data["balance"] == 0.0


def test_get_balance_integration(client, auth_header):
    _override_current_user_mock(client)
    with patch("app.crud.movement.movement_crud.get_balance", return_value={
        "total_income": 1500.0, "total_expense": 500.0, "balance": 1000.0,
    }):
        resp = client.get("/movements/balance")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["total_income"] == 1500.0
    assert data["total_expense"] == 500.0
    assert data["balance"] == 1000.0


def test_movement_ownership(client, auth_header):
    cat_id = _create_category(client, auth_header)
    _create_income(client, auth_header, cat_id)
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
