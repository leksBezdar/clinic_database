import jwt
import uuid

from fastapi import Depends

from .models import User
from .utils import OAuth2PasswordBearerWithCookie
from .service import UserService
from .exceptions import InvalidToken
from ..config import settings

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/login")


async def get_current_user(
        token: str = Depends(oauth2_scheme)
) -> User | None:
    try:
        payload = jwt.decode(token,
                             settings.TOKEN_SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise InvalidToken
    except Exception:
        raise InvalidToken
    current_user = await UserService.get_user(uuid.UUID(user_id))
    
    return current_user