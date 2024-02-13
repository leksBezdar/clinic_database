from .models import User, RefreshToken
from .schemas import RefreshTokenCreate, RefreshTokenUpdate, UserCreateDB, UserUpdate

from ..dao import BaseDAO


class UserDAO(BaseDAO[User, UserCreateDB, UserUpdate]):
    model = User


class RefreshTokenDAO(BaseDAO[RefreshToken, RefreshTokenCreate, RefreshTokenUpdate]):
    model = RefreshToken
