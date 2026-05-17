from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_refresh_token,
    verify_password,
)
from app.crud.refresh_token import refresh_token_crud
from app.crud.user import user_crud
from app.schemas.auth import LoginRequest, RegisterRequest


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register(self, body: RegisterRequest) -> dict | None:
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
        access_token = create_access_token({"sub": str(user.id)})
        raw_refresh, refresh_hash = generate_refresh_token()
        refresh_token_crud.create(
            self.db,
            user_id=user.id,
            token_hash=refresh_hash,
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=settings.refresh_token_expire_days),
        )
        return {"access_token": access_token, "refresh_token": raw_refresh}

    def login(self, body: LoginRequest) -> dict | None:
        user = user_crud.get_by_email(self.db, body.email)
        if not user or not verify_password(body.password, user.pwd_hash):
            return None
        user.last_login_at = datetime.now(timezone.utc)
        self.db.commit()
        access_token = create_access_token({"sub": str(user.id)})
        raw_refresh, refresh_hash = generate_refresh_token()
        refresh_token_crud.create(
            self.db,
            user_id=user.id,
            token_hash=refresh_hash,
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=settings.refresh_token_expire_days),
        )
        return {"access_token": access_token, "refresh_token": raw_refresh}

    def refresh(self, raw_token: str) -> dict | None:
        token_hash = hash_refresh_token(raw_token)
        stored = refresh_token_crud.get_by_token_hash(self.db, token_hash)
        if not stored:
            return None
        if stored.revoked_at is not None:
            return None
        if stored.expires_at < datetime.now(timezone.utc):
            return None

        stored.revoked_at = datetime.now(timezone.utc)
        self.db.commit()

        access_token = create_access_token({"sub": str(stored.user_id)})
        new_raw, new_hash = generate_refresh_token()
        refresh_token_crud.create(
            self.db,
            user_id=stored.user_id,
            token_hash=new_hash,
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=settings.refresh_token_expire_days),
        )
        return {"access_token": access_token, "refresh_token": new_raw}

    def logout(self, raw_token: str) -> bool:
        token_hash = hash_refresh_token(raw_token)
        stored = refresh_token_crud.get_by_token_hash(self.db, token_hash)
        if not stored:
            return False
        stored.revoked_at = datetime.now(timezone.utc)
        self.db.commit()
        return True
