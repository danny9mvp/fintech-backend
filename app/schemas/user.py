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
    firstname: str | None = None
    middlename: str | None = None
    lastname: str | None = None
    second_lastname: str | None = None

class UserResponse(UserBase):
    id: int
    firstname: str
    middlename: str | None
    lastname: str
    second_lastname: str | None

    model_config = {"from_attributes": True}
