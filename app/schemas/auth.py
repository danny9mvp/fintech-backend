from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    username: str
    firstname: str | None = None
    middlename: str | None = None
    lastname: str | None = None
    second_lastname: str | None = None
