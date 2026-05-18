from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.model.movement_category import MovementCategory


class CRUDMovementCategory(CRUDBase):
    def __init__(self):
        super().__init__(MovementCategory)

    def get_by_user(
        self, db: Session, user_id: int, offset: int = 0, limit: int = 100
    ):
        return (
            db.query(MovementCategory)
            .filter(MovementCategory.user_id == user_id)
            .offset(offset)
            .limit(limit)
            .all()
        )


category_crud = CRUDMovementCategory()
