from math import ceil

from sqlalchemy.orm import Session

from app.crud.movement import movement_crud
from app.crud.movement_category import category_crud
from app.model.user import User
from app.schemas.movement import MovementCreate, MovementResponse, MovementUpdate
from app.schemas.paginated import PaginatedResponse


class MovementService:
    def __init__(self, db: Session, current_user: User):
        self.db = db
        self.user = current_user

    def _get_entity(self, movement_id: int):
        obj = movement_crud.get(self.db, movement_id)
        if not obj or obj.user_id != self.user.id:
            return None
        return obj

    def list(
        self,
        page: int = 1,
        page_size: int = 10,
        movement_type: str | None = None,
        category_id: int | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ):
        offset = (page - 1) * page_size
        total = movement_crud.count_user_movements(
            self.db, user_id=self.user.id,
            movement_type=movement_type, category_id=category_id,
            date_from=date_from, date_to=date_to,
        )
        items = (
            movement_crud.get_by_user(
                self.db, user_id=self.user.id, offset=offset, limit=page_size,
                movement_type=movement_type, category_id=category_id,
                date_from=date_from, date_to=date_to,
            )
            if total > 0
            else []
        )
        total_pages = ceil(total / page_size) if total > 0 else 0
        return PaginatedResponse(
            items=[MovementResponse.model_validate(m) for m in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )

    def create(self, body: MovementCreate):
        category = category_crud.get(self.db, body.movement_category_id)
        if not category or category.user_id != self.user.id:
            return None
        data = body.model_dump()
        data["type"] = data["type"].upper()
        if data["type"] == "EXPENSE":
            balance = movement_crud.get_balance(self.db, self.user.id)
            if data["amount"] > balance["balance"]:
                raise ValueError("Insufficient balance to create this expense")
        obj = movement_crud.create(self.db, user_id=self.user.id, **data)
        return MovementResponse.model_validate(obj)

    def get_balance(self):
        return movement_crud.get_balance(self.db, user_id=self.user.id)

    def get(self, movement_id: int):
        obj = self._get_entity(movement_id)
        return MovementResponse.model_validate(obj) if obj else None

    def update(self, movement_id: int, body: MovementUpdate):
        obj = self._get_entity(movement_id)
        if not obj:
            return None
        updated = movement_crud.update(self.db, obj, **body.model_dump())
        return MovementResponse.model_validate(updated)

    def delete(self, movement_id: int) -> bool:
        obj = self._get_entity(movement_id)
        if not obj:
            return False
        movement_crud.remove(self.db, movement_id)
        return True
