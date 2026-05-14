from datetime import datetime

from pydantic import BaseModel


class UserBase(BaseModel):
    email: str
    username: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
