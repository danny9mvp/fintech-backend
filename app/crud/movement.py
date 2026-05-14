from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.model.movement import Movement


class CRUDMovement(CRUDBase):
    def __init__(self):
        super().__init__(Movement)

    def count_user_movements(self, db: Session, user_id: int):
        return db.query(Movement).filter(Movement.user_id == user_id).count()

    def get_by_user(
        self, db: Session, user_id: int, offset, limit
    ):
        return (
            db.query(Movement)
            .filter(Movement.user_id == user_id)
            .order_by(Movement.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )


movement_crud = CRUDMovement()
