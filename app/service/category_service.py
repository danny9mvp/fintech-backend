from sqlalchemy.orm import Session

from app.crud.movement import movement_crud
from app.crud.movement_category import category_crud
from app.model.user import User
from app.schemas.budget_warning import BudgetWarningResponse
from app.schemas.movement_category import CategoryCreate, CategoryResponse, CategoryUpdate


class CategoryService:
    def __init__(self, db: Session, current_user: User):
        self.db = db
        self.user = current_user

    def _get_entity(self, category_id: int):
        obj = category_crud.get(self.db, category_id)
        if not obj or obj.user_id != self.user.id:
            return None
        return obj

    def get_budget_warning(self, category_id: int) -> BudgetWarningResponse | None:
        category = self._get_entity(category_id)
        if not category:
            return None
        return self._build_warning(category)

    def _build_warning(self, category) -> BudgetWarningResponse:
        if not category.budget or category.budget <= 0:
            return BudgetWarningResponse(
                category_id=category.id,
                category_name=category.name,
                budget=category.budget,
                total_expense=0.0,
                usage_percentage=None,
                warning_level="no_budget",
                message=f"No hay presupuesto asignado para '{category.name}'",
            )
        total = movement_crud.get_category_expense(
            self.db, category.id, self.user.id
        )
        pct = (total / category.budget) * 100
        msg = "Has usado el {} del presupuesto para {}"
        if pct >= 100:
            level = "exceeded"
        elif pct >= 80:
            level = "warning"
        else:
            level = "none"
        return BudgetWarningResponse(
            category_id=category.id,
            category_name=category.name,
            budget=category.budget,
            total_expense=total,
            usage_percentage=round(pct, 2),
            warning_level=level,
            message=msg.format(f"{pct:.1f}%", category.name)
        )

    def list(self, offset: int = 0, limit: int = 100):
        objs = category_crud.get_by_user(self.db, user_id=self.user.id, offset=offset, limit=limit)
        return [CategoryResponse.model_validate(o) for o in objs]

    def create(self, body: CategoryCreate):
        obj = category_crud.create(self.db, user_id=self.user.id, **body.model_dump())
        return CategoryResponse.model_validate(obj)

    def get(self, category_id: int):
        obj = self._get_entity(category_id)
        return CategoryResponse.model_validate(obj) if obj else None

    def update(self, category_id: int, body: CategoryUpdate):
        obj = self._get_entity(category_id)
        if not obj:
            return None
        updated = category_crud.update(self.db, obj, **body.model_dump())
        return CategoryResponse.model_validate(updated)

    def delete(self, category_id: int) -> bool:
        obj = self._get_entity(category_id)
        if not obj:
            return False
        category_crud.remove(self.db, category_id)
        return True
