from datetime import date

from sqlalchemy.orm import Session, joinedload, load_only, contains_eager

from app.crud.base import CRUDBase
from app.model.movement import Movement


class CRUDMovement(CRUDBase):
    def __init__(self):
        super().__init__(Movement)

    def count_user_movements(self,
                             db: Session,
                             user_id: int,
                             movement_type: str | None = None,
                             category_id: int | None = None,
                             date_from: date | None = None,
                             date_to: date | None = None
                             ):
        query = db.query(Movement).filter(Movement.user_id == user_id)
        filtered_query = self._chain_query(query, movement_type, category_id, date_from, date_to)

        return filtered_query.count()

    def get_by_user(self,
                    db: Session,
                    user_id: int,
                    offset,
                    limit,
                    movement_type: str | None = None,
                    category_id: int | None = None,
                    date_from: date | None = None,
                    date_to: date | None = None,
    ):
        query = (db.query(Movement)
                 .options(load_only(Movement.id, Movement.type, Movement.amount, Movement.description, Movement.created_at, Movement.movement_category_id)).filter(Movement.user_id == user_id)
                 .options(contains_eager(Movement.category))
                 .join(Movement.category)
                 .filter(Movement.user_id == user_id))
        filtered_query = self._chain_query(query, movement_type, category_id, date_from, date_to)

        return (
            filtered_query
            .order_by(Movement.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def _chain_query(self, query, movement_type, category_id, date_from, date_to):
        if movement_type:
            query = query.filter(Movement.type == movement_type)
        if category_id:
            query = query.filter(Movement.movement_category_id == category_id)
        if date_from:
            query = query.filter(Movement.created_at >= date_from)
        if date_to:
            query = query.filter(Movement.created_at <= date_to)

        return query

movement_crud = CRUDMovement()
