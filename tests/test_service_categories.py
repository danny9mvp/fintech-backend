from datetime import datetime
from unittest.mock import MagicMock, patch

from app.service.category_service import CategoryService
from app.schemas.movement_category import CategoryResponse


def _mock_category(id=1, user_id=1, name="Default", budget=100.0):
    c = MagicMock()
    c.id = id
    c.user_id = user_id
    c.name = name
    c.budget = budget
    c.created_at = datetime.now()
    return c


class TestCategoryServiceList:
    def test_returns_list_of_category_responses(self):
        db = MagicMock()
        user = MagicMock()
        user.id = 1
        mock_cat = _mock_category(id=1, name="Food", budget=300.0)

        with patch("app.service.category_service.category_crud") as crud:
            crud.get_by_user.return_value = [mock_cat]
            result = CategoryService(db, user).list()

        assert len(result) == 1
        assert isinstance(result[0], CategoryResponse)
        assert result[0].name == "Food"
        assert result[0].budget == 300.0
        assert result[0].id == 1

    def test_returns_empty_list_when_no_categories(self):
        db = MagicMock()
        user = MagicMock()
        user.id = 1

        with patch("app.service.category_service.category_crud") as crud:
            crud.get_by_user.return_value = []
            result = CategoryService(db, user).list()

        assert result == []


class TestCategoryServiceCreate:
    def test_returns_category_response(self):
        db = MagicMock()
        user = MagicMock()
        user.id = 1
        mock_cat = _mock_category(id=10, name="New", budget=50.0)
        body = MagicMock()
        body.model_dump.return_value = {"name": "New", "budget": 50.0}

        with patch("app.service.category_service.category_crud") as crud:
            crud.create.return_value = mock_cat
            result = CategoryService(db, user).create(body)

        assert isinstance(result, CategoryResponse)
        assert result.name == "New"
        assert result.budget == 50.0
        assert result.id == 10


class TestCategoryServiceGet:
    def test_returns_category_response_when_found_and_owned(self):
        db = MagicMock()
        user = MagicMock()
        user.id = 1
        mock_cat = _mock_category(id=5, name="Rent", budget=1000.0)

        with patch("app.service.category_service.category_crud") as crud:
            crud.get.return_value = mock_cat
            result = CategoryService(db, user).get(5)

        assert isinstance(result, CategoryResponse)
        assert result.name == "Rent"
        assert result.budget == 1000.0

    def test_returns_none_when_not_found(self):
        db = MagicMock()
        user = MagicMock()
        user.id = 1

        with patch("app.service.category_service.category_crud") as crud:
            crud.get.return_value = None
            result = CategoryService(db, user).get(999)

        assert result is None

    def test_returns_none_when_not_owned(self):
        db = MagicMock()
        user = MagicMock()
        user.id = 2
        mock_cat = _mock_category(id=1, user_id=1)

        with patch("app.service.category_service.category_crud") as crud:
            crud.get.return_value = mock_cat
            result = CategoryService(db, user).get(1)

        assert result is None


class TestCategoryServiceUpdate:
    def test_returns_updated_category_response(self):
        db = MagicMock()
        user = MagicMock()
        user.id = 1
        mock_cat = _mock_category(id=2, name="Old", budget=100.0)
        mock_updated = _mock_category(id=2, name="Updated", budget=200.0)
        body = MagicMock()
        body.model_dump.return_value = {"name": "Updated", "budget": 200.0}

        with patch("app.service.category_service.category_crud") as crud:
            crud.get.return_value = mock_cat
            crud.update.return_value = mock_updated
            result = CategoryService(db, user).update(2, body)

        assert isinstance(result, CategoryResponse)
        assert result.name == "Updated"
        assert result.budget == 200.0
        crud.update.assert_called_once()

    def test_returns_none_when_not_found(self):
        db = MagicMock()
        user = MagicMock()
        user.id = 1
        body = MagicMock()

        with patch("app.service.category_service.category_crud") as crud:
            crud.get.return_value = None
            result = CategoryService(db, user).update(999, body)

        assert result is None
        crud.update.assert_not_called()


class TestCategoryServiceDelete:
    def test_returns_true_and_removes(self):
        db = MagicMock()
        user = MagicMock()
        user.id = 1
        mock_cat = _mock_category(id=3)

        with patch("app.service.category_service.category_crud") as crud:
            crud.get.return_value = mock_cat
            result = CategoryService(db, user).delete(3)

        assert result is True
        crud.remove.assert_called_once_with(db, 3)

    def test_returns_false_when_not_found(self):
        db = MagicMock()
        user = MagicMock()
        user.id = 1

        with patch("app.service.category_service.category_crud") as crud:
            crud.get.return_value = None
            result = CategoryService(db, user).delete(999)

        assert result is False
        crud.remove.assert_not_called()

    def test_returns_false_when_not_owned(self):
        db = MagicMock()
        user = MagicMock()
        user.id = 2
        mock_cat = _mock_category(id=1, user_id=1)

        with patch("app.service.category_service.category_crud") as crud:
            crud.get.return_value = mock_cat
            result = CategoryService(db, user).delete(1)

        assert result is False
        crud.remove.assert_not_called()
