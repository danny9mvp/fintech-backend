from sqlalchemy.orm import Session

from app.crud.movement_category import category_crud
from app.model.user import User
from app.schemas.movement_category import CategoryCreate, CategoryUpdate


class CategoryService:
    def __init__(self, db: Session, current_user: User):
        self.db = db
        self.user = current_user

    def list(self, offset: int = 0, limit: int = 100):
        return category_crud.get_by_user(self.db, user_id=self.user.id, offset=offset, limit=limit)

    def create(self, body: CategoryCreate):
        return category_crud.create(self.db, user_id=self.user.id, **body.model_dump())

    def get(self, category_id: int):
        obj = category_crud.get(self.db, category_id)
        if not obj or obj.user_id != self.user.id:
            return None
        return obj

    def update(self, category_id: int, body: CategoryUpdate):
        obj = self.get(category_id)
        if not obj:
            return None
        return category_crud.update(self.db, obj, **body.model_dump())

    def delete(self, category_id: int) -> bool:
        obj = self.get(category_id)
        if not obj:
            return False
        category_crud.remove(self.db, category_id)
        return True
