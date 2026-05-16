from sqlalchemy.orm import Session

from app.crud.user import user_crud
from app.model.user import User
from app.schemas.user import UserUpdate


class UserService:
    def __init__(self, db: Session, current_user: User):
        self.db = db
        self.user = current_user

    def update(self, body: UserUpdate):
        return user_crud.update(self.db, self.user, **body.model_dump())
