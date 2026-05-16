from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.crud.user import user_crud
from app.schemas.auth import LoginRequest, RegisterRequest


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register(self, body: RegisterRequest) -> str | None:
        existing = user_crud.get_by_email(self.db, body.email)
        if existing:
            return None
        user = user_crud.create(
            self.db, email=body.email, password=body.password, username=body.username,
            firstname=body.firstname or "",
            lastname=body.lastname or "",
            middlename=body.middlename,
            second_lastname=body.second_lastname,
        )
        return create_access_token({"sub": str(user.id)})

    def login(self, body: LoginRequest) -> str | None:
        user = user_crud.get_by_email(self.db, body.email)
        if not user or not verify_password(body.password, user.pwd_hash):
            return None
        user.last_login_at = datetime.now(timezone.utc)
        self.db.commit()
        return create_access_token({"sub": str(user.id)})
