import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt as _bcrypt
from jwt import decode, encode

from app.core.config import settings


def hash_password(password: str) -> str:
    return _bcrypt.hashpw(password.encode(), _bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return _bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    to_encode.update({"exp": expire})
    return encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict | None:
    try:
        return decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except Exception:
        return None


def generate_refresh_token() -> tuple[str, str]:
    token = secrets.token_hex(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    return token, token_hash


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
