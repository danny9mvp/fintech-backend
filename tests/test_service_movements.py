from datetime import datetime
from unittest.mock import MagicMock, patch

from app.service.movement_service import MovementService
from app.schemas.movement import MovementResponse
from app.schemas.paginated import PaginatedResponse


def _mock_movement(
    id=1,
    user_id=1,
    movement_type="INCOME",
    amount=100.0,
    description=None,
    movement_category_id=1,
    category_name="Salary",
):
    m = MagicMock()
    m.id = id
    m.user_id = user_id
    m.type = movement_type
    m.amount = amount
    m.description = description
    m.movement_category_id = movement_category_id
    m.category_name = category_name
    m.created_at = datetime.now()
    return m


def _mock_category(id=1, user_id=1):
    c = MagicMock()
    c.id = id
    c.user_id = user_id
    return c


class TestMovementServiceList:
    def test_returns_paginated_response_with_movement_responses(self):
        db = MagicMock()
        user = MagicMock()
        user.id = 1
        mock_m = _mock_movement(id=1, amount=500.0, category_name="Freelance")

        with patch("app.service.movement_service.movement_crud") as m_crud:
            m_crud.count_user_movements.return_value = 1
            m_crud.get_by_user.return_value = [mock_m]
            result = MovementService(db, user).list()

        assert isinstance(result, PaginatedResponse)
        assert result.total == 1
        assert result.page == 1
        assert len(result.items) == 1
        assert isinstance(result.items[0], MovementResponse)
        assert result.items[0].amount == 500.0
        assert result.items[0].category_name == "Freelance"

    def test_pagination_metadata_is_correct(self):
        db = MagicMock()
        user = MagicMock()
        user.id = 1
        mock_m = _mock_movement(id=1)

        with patch("app.service.movement_service.movement_crud") as m_crud:
            m_crud.count_user_movements.return_value = 25
            m_crud.get_by_user.return_value = [mock_m] * 10
            result = MovementService(db, user).list(page=2, page_size=10)

        assert result.total == 25
        assert result.page == 2
        assert result.page_size == 10
        assert result.total_pages == 3
        assert result.has_next is True
        assert result.has_prev is True
        assert len(result.items) == 10

    def test_has_next_false_on_last_page(self):
        db = MagicMock()
        user = MagicMock()
        user.id = 1

        with patch("app.service.movement_service.movement_crud") as m_crud:
            m_crud.count_user_movements.return_value = 10
            m_crud.get_by_user.return_value = [_mock_movement(id=i) for i in range(10)]
            result = MovementService(db, user).list(page=1, page_size=10)

        assert result.has_next is False
        assert result.has_prev is False
        assert result.total_pages == 1

    def test_returns_empty_when_no_movements(self):
        db = MagicMock()
        user = MagicMock()
        user.id = 1

        with patch("app.service.movement_service.movement_crud") as m_crud:
            m_crud.count_user_movements.return_value = 0
            result = MovementService(db, user).list()

        assert result.total == 0
        assert result.items == []
        assert result.total_pages == 0

    def test_forwards_filters_to_crud(self):
        db = MagicMock()
        user = MagicMock()
        user.id = 1

        with patch("app.service.movement_service.movement_crud") as m_crud:
            m_crud.count_user_movements.return_value = 0
            MovementService(db, user).list(
                movement_type="EXPENSE",
                category_id=3,
                date_from="2024-01-01",
                date_to="2024-12-31",
            )

        m_crud.count_user_movements.assert_called_once_with(
            db, user_id=1,
            movement_type="EXPENSE", category_id=3,
            date_from="2024-01-01", date_to="2024-12-31",
        )


class TestMovementServiceCreate:
    def test_returns_movement_response_on_success(self):
        db = MagicMock()
        user = MagicMock()
        user.id = 1
        mock_category = _mock_category(id=5, user_id=1)
        mock_movement = _mock_movement(id=1, amount=200.0)
        body = MagicMock()
        body.movement_category_id = 5
        body.model_dump.return_value = {
            "type": "INCOME", "amount": 200.0,
            "movement_category_id": 5,
        }

        with patch("app.service.movement_service.movement_crud") as m_crud, \
             patch("app.service.movement_service.category_crud") as c_crud:
            c_crud.get.return_value = mock_category
            m_crud.create.return_value = mock_movement
            result = MovementService(db, user).create(body)

        assert isinstance(result, MovementResponse)
        assert result.amount == 200.0

    def test_returns_none_when_category_not_found(self):
        db = MagicMock()
        user = MagicMock()
        user.id = 1
        body = MagicMock()
        body.movement_category_id = 999

        with patch("app.service.movement_service.category_crud") as c_crud:
            c_crud.get.return_value = None
            result = MovementService(db, user).create(body)

        assert result is None

    def test_returns_none_when_category_not_owned(self):
        db = MagicMock()
        user = MagicMock()
        user.id = 2
        mock_category = _mock_category(id=1, user_id=1)
        body = MagicMock()
        body.movement_category_id = 1

        with patch("app.service.movement_service.category_crud") as c_crud:
            c_crud.get.return_value = mock_category
            result = MovementService(db, user).create(body)

        assert result is None


class TestMovementServiceGetBalance:
    def test_returns_balance_dict(self):
        db = MagicMock()
        user = MagicMock()
        user.id = 1
        expected = {"total_income": 1000.0, "total_expense": 400.0, "balance": 600.0}

        with patch("app.service.movement_service.movement_crud") as m_crud:
            m_crud.get_balance.return_value = expected
            result = MovementService(db, user).get_balance()

        assert result == expected
        m_crud.get_balance.assert_called_once_with(db, user_id=1)


class TestMovementServiceGet:
    def test_returns_movement_response_when_found_and_owned(self):
        db = MagicMock()
        user = MagicMock()
        user.id = 1
        mock_m = _mock_movement(id=7, amount=150.0)

        with patch("app.service.movement_service.movement_crud") as m_crud:
            m_crud.get.return_value = mock_m
            result = MovementService(db, user).get(7)

        assert isinstance(result, MovementResponse)
        assert result.amount == 150.0
        assert result.id == 7

    def test_returns_none_when_not_found(self):
        db = MagicMock()
        user = MagicMock()
        user.id = 1

        with patch("app.service.movement_service.movement_crud") as m_crud:
            m_crud.get.return_value = None
            result = MovementService(db, user).get(999)

        assert result is None

    def test_returns_none_when_not_owned(self):
        db = MagicMock()
        user = MagicMock()
        user.id = 2
        mock_m = _mock_movement(id=1, user_id=1)

        with patch("app.service.movement_service.movement_crud") as m_crud:
            m_crud.get.return_value = mock_m
            result = MovementService(db, user).get(1)

        assert result is None


class TestMovementServiceUpdate:
    def test_returns_updated_movement_response(self):
        db = MagicMock()
        user = MagicMock()
        user.id = 1
        mock_m = _mock_movement(id=3, amount=100.0)
        mock_updated = _mock_movement(id=3, amount=300.0)
        body = MagicMock()
        body.model_dump.return_value = {"amount": 300.0}

        with patch("app.service.movement_service.movement_crud") as m_crud:
            m_crud.get.return_value = mock_m
            m_crud.update.return_value = mock_updated
            result = MovementService(db, user).update(3, body)

        assert isinstance(result, MovementResponse)
        assert result.amount == 300.0
        m_crud.update.assert_called_once()

    def test_returns_none_when_not_found(self):
        db = MagicMock()
        user = MagicMock()
        user.id = 1
        body = MagicMock()

        with patch("app.service.movement_service.movement_crud") as m_crud:
            m_crud.get.return_value = None
            result = MovementService(db, user).update(999, body)

        assert result is None
        m_crud.update.assert_not_called()

    def test_respects_ownership(self):
        db = MagicMock()
        user = MagicMock()
        user.id = 2
        mock_m = _mock_movement(id=1, user_id=1)
        body = MagicMock()

        with patch("app.service.movement_service.movement_crud") as m_crud:
            m_crud.get.return_value = mock_m
            result = MovementService(db, user).update(1, body)

        assert result is None
        m_crud.update.assert_not_called()


class TestMovementServiceDelete:
    def test_returns_true_and_removes(self):
        db = MagicMock()
        user = MagicMock()
        user.id = 1
        mock_m = _mock_movement(id=4)

        with patch("app.service.movement_service.movement_crud") as m_crud:
            m_crud.get.return_value = mock_m
            result = MovementService(db, user).delete(4)

        assert result is True
        m_crud.remove.assert_called_once_with(db, 4)

    def test_returns_false_when_not_found(self):
        db = MagicMock()
        user = MagicMock()
        user.id = 1

        with patch("app.service.movement_service.movement_crud") as m_crud:
            m_crud.get.return_value = None
            result = MovementService(db, user).delete(999)

        assert result is False
        m_crud.remove.assert_not_called()

    def test_returns_false_when_not_owned(self):
        db = MagicMock()
        user = MagicMock()
        user.id = 2
        mock_m = _mock_movement(id=1, user_id=1)

        with patch("app.service.movement_service.movement_crud") as m_crud:
            m_crud.get.return_value = mock_m
            result = MovementService(db, user).delete(1)

        assert result is False
        m_crud.remove.assert_not_called()
