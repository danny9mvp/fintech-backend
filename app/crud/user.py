from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.crud.base import CRUDBase
from app.model.user import User


class CRUDUser(CRUDBase):
    def __init__(self):
        super().__init__(User)

    def get_by_email(self, db: Session, email: str) -> User | None:
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, **kwargs) -> User:
        kwargs["pwd_hash"] = hash_password(kwargs.pop("password"))
        return super().create(db, **kwargs)


user_crud = CRUDUser()
