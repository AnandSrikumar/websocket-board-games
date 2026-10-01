import re
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


class Register(BaseModel):
    username: str = Field(max_length=50, min_length=3)
    password: str = Field(min_length=8, max_length=24)
    email: EmailStr

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str) -> str:
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter")

        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain at least one lowercase letter")

        if not re.search(r"\d", password):
            raise ValueError("Password must contain at least one digit")

        if not re.search(r"[^A-Za-z0-9]", password):
            raise ValueError("Password must contain at least one special character")

        return password


class RegisterSuccess(BaseModel):
    id: UUID
    username: str


class Login(BaseModel):
    identifier: str
    password: str


class LoginSuccess(BaseModel):
    access_token: str
    token_type: str = "bearer"
