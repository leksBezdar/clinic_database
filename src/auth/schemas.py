from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from ..config import settings


class UserBase(BaseModel):
    username: str
    is_superuser: bool = Field(False)
    is_active: bool = Field(True)

class UserCreate(UserBase):
    username: str
    password: str

    @field_validator("username")
    def validate_username_length(cls, value):
        if len(value) < int(settings.MIN_USERNAME_LENGTH) or len(value) > int(settings.MAX_USERNAME_LENGTH):
            raise ValueError("Username must be between 5 and 15 characters")

        return value

    @field_validator("password")
    def validate_password_complexity(cls, value):
        if len(value) < int(settings.MIN_PASSWORD_LENGTH) or len(value) > int(settings.MAX_PASSWORD_LENGTH):
            raise ValueError("Password must be between 8 and 30 characters")

        return value

class UserCreateDB(UserBase):
    hashed_password: str

class UserUpdate(BaseModel):
    username: str | None = None
    hashed_password: str | None = None
    is_superuser: bool | None = None
    

class UserGet(UserBase):
    id: UUID

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
    

class LoginIn(BaseModel):
    username: str
    password: str    

class LoginResponse(BaseModel):
    user: UserGet
    tokens: Token