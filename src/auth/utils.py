import hashlib
import random
import string

from fastapi import HTTPException, Request, status
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param

from . import exceptions
from ..config import settings


class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: str | None = None,
        scopes: dict[str, str] | None = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(
            password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> str | None:
        authorization: str = request.cookies.get("access_token")

        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param


async def get_random_string(length: int = 16) -> str:
    """Generates a random string used as a salt.

    Args:
        length (int, optional): Length of the random string. Defaults to 16.

    Returns:
        str: Randomly generated string.
    """
    return "".join(random.choice(string.ascii_letters) for _ in range(length))


async def validate_password(password: str, hashed_password: str) -> None:
    """Validates that the password hash matches the hash from the database.

    Args:
        password (str): The password to validate.
        hashed_password (str): The hashed password stored in the database.

    Raises:
        exceptions.InvalidAuthenthicationCredential: If the password validation fails.
    """
    salt, hashed = hashed_password.split(settings.PASSWORD_SALT_SEPARATOR)

    if not await __hash_password(password, salt) == hashed:
        raise exceptions.InvalidAuthenthicationCredential
    
    return {"Message": "Password is valid"}



async def __hash_password(password: str, salt: str = None) -> str:
    """Hashes a password using salt and hashlib.

    Args:
        password (str): The password to hash.
        salt (str, optional): The salt used for hashing. If not provided, generates a random salt. Defaults to None.

    Returns:
        str: The hashed password.
    """
    if salt is None:
        salt = await get_random_string()
    enc = hashlib.pbkdf2_hmac(
        settings.PASSWORD_HASH_NAME, password.encode(), salt.encode(), settings.PASSWORD_HASH_ITERATIONS)

    return enc.hex()


async def get_hashed_password(password: str) -> str:
    """Gets the hashed password.

    Args:
        password (str): The password to hash.

    Returns:
        str: The hashed password with salt appended.
    """
    salt = await get_random_string()
    hashed_password = await __hash_password(password, salt)
    
    return f"{salt}${hashed_password}"


