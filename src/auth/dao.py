from ..dao import BaseDAO
from .models import RefreshToken, User
from .schemas import RefreshTokenCreate, RefreshTokenUpdate, UserCreateDB, UserUpdate


class UserDAO(BaseDAO[User, UserCreateDB, UserUpdate]):
    model = User


class RefreshTokenDAO(BaseDAO[RefreshToken, RefreshTokenCreate, RefreshTokenUpdate]):
    model = RefreshToken
