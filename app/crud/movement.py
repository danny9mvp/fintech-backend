from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.model.movement import Movement


class CRUDMovement(CRUDBase):
    def __init__(self):
        super().__init__(Movement)

    def get_by_user(
        self, db: Session, user_id: int, skip: int = 0, limit: int = 100
    ):
        return (
            db.query(Movement)
            .filter(Movement.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )


movement_crud = CRUDMovement()
