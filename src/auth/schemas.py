from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from ..config import settings


class UserRole(str, Enum):
    therapist = "therapist"
    explorer = "explorer"


class UserBase(BaseModel):
    username: str
    role: UserRole


class UserCreate(UserBase):
    username: str
    password: str

    @field_validator("username")
    def validate_username_length(cls, value):
        if len(value) < int(settings.MIN_USERNAME_LENGTH) or len(value) > int(settings.MAX_USERNAME_LENGTH):
            raise ValueError(
                f"Username must be between {settings.MIN_USERNAME_LENGTH} and {settings.MAX_USERNAME_LENGTH} characters"
            )

        return value

    @field_validator("password")
    def validate_password_complexity(cls, value):
        if len(value) < int(settings.MIN_PASSWORD_LENGTH) or len(value) > int(settings.MAX_PASSWORD_LENGTH):
            raise ValueError(
                f"Password must be between {settings.MIN_PASSWORD_LENGTH} and {settings.MAX_PASSWORD_LENGTH} characters"
            )

        return value


class UserCreateDB(UserBase):
    is_superuser: bool = False
    hashed_password: str


class UserUpdate(BaseModel):
    username: str | None = None
    role: UserRole | None = None
    hashed_password: str | None = None


class ChangeUserPassword(BaseModel):
    old_password: str
    new_password: str


class UserGet(UserBase):
    id: UUID
    is_superuser: bool
    is_active: bool

    class Config:
        from_attributes = True


class RefreshTokenCreate(BaseModel):
    refresh_token: UUID
    expires_in: int
    user_id: UUID


class RefreshTokenUpdate(RefreshTokenCreate):
    user_id: str | None = Field(None)


class Token(BaseModel):
    access_token: str
    refresh_token: UUID
    token_type: str = "Bearer"


class LoginIn(BaseModel):
    username: str
    password: str
