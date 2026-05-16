from math import ceil

from sqlalchemy.orm import Session

from app.crud.movement import movement_crud
from app.crud.movement_category import category_crud
from app.model.user import User
from app.schemas.movement import MovementCreate, MovementUpdate
from app.schemas.paginated import PaginatedResponse


class MovementService:
    def __init__(self, db: Session, current_user: User):
        self.db = db
        self.user = current_user

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
            items=items,
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
        return movement_crud.create(self.db, user_id=self.user.id, **body.model_dump())

    def get_balance(self):
        return movement_crud.get_balance(self.db, user_id=self.user.id)

    def get(self, movement_id: int):
        obj = movement_crud.get(self.db, movement_id)
        if not obj or obj.user_id != self.user.id:
            return None
        return obj

    def update(self, movement_id: int, body: MovementUpdate):
        obj = self.get(movement_id)
        if not obj:
            return None
        return movement_crud.update(self.db, obj, **body.model_dump())

    def delete(self, movement_id: int) -> bool:
        obj = self.get(movement_id)
        if not obj:
            return False
        movement_crud.remove(self.db, movement_id)
        return True
