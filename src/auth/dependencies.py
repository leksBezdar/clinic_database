import jwt
import uuid

from fastapi import Depends

from .models import User
from .utils import OAuth2PasswordBearerWithCookie
from .service import UserService
from . import exceptions
from ..config import settings

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/login")


async def get_current_user(
        token: str = Depends(oauth2_scheme)
) -> User | None:
    try:
        payload: dict = jwt.decode(token, settings.TOKEN_SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise exceptions.InvalidToken
    except Exception:
        raise exceptions.InvalidToken
    current_user = await UserService.get_user(uuid.UUID(user_id))
    
    return current_user


async def get_current_superuser(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_superuser:
        raise exceptions.Forbidden
    return current_user