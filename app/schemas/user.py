from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: str
    username: str


class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None

class UserResponse(UserBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
