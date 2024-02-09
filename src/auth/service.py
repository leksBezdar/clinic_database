import jwt

from datetime import datetime, timedelta, timezone

from fastapi import Response
from fastapi.responses import JSONResponse

from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from . import models, exceptions, schemas, utils
from .config import (
    TOKEN_SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS
)
from .dao import RefreshTokenDAO, UserDAO
from .models import Refresh_token, User

from ..utils import get_unique_id


class UserCRUD:

    async def create_user(self, user: schemas.UserCreate) -> models.User:

        if await self.get_existing_user(username=user.username):
            raise exceptions.UserAlreadyExists
        id = await get_unique_id()

        hashed_password = await utils.get_hashed_password(user.password)

        # Создание экземпляра User с предоставленными данными
        db_user = await UserDAO.add(
            schemas.UserCreateDB(
                **user.model_dump(),
                id=id,
                hashed_password=hashed_password
            )
        )
        return db_user

    async def authenticate_user(self, username: str, password: str) -> User:

        try:

            user = await self.get_existing_user(username=username)
            await utils.validate_password(password=password, hashed_password=user.hashed_password)

            return user

        except AttributeError:
            raise exceptions.InvalidAuthenthicationCredential

    async def logout(self, refresh_token: str = None) -> JSONResponse:

        if not refresh_token:
            return exceptions.InactiveUser

        refresh_session = await RefreshTokenDAO.find_one_or_none(Refresh_token.refresh_token == refresh_token)

        if refresh_session:
            await RefreshTokenDAO.delete(id=refresh_session.id)

        response = JSONResponse(content={
            "message": "logout successful",
        })

        response.delete_cookie(key="access_token")
        response.delete_cookie(key="refresh_token")

        return response

    async def get_existing_user(self, username: str = None, user_id: str = None, token: str = None) -> User:
        if not username and not user_id and not token:
            raise exceptions.NoUserData

        if token:
            user_id = await TokenCrud.get_access_token_payload(access_token=token)

        user = await UserDAO.find_one_or_none(or_(
            User.username == username,
            User.id == user_id))
        
        return user

    # Получение списка всех пользователей с поддержкой пагинации
    async def get_all_users(self, *filter, offset: int = 0, limit: int = 100, **filter_by) -> list[User]:

        users = await UserDAO.find_all(*filter, offset=offset, limit=limit, **filter_by)

        return users

    async def _get_refresh_token_by_user_id(self, user: models.User) -> models.Refresh_token:

        refresh_token = await RefreshTokenDAO.find_one_or_none(Refresh_token.user_id == user.id)

        return refresh_token

    async def get_user_by_access_token(self, access_token: str) -> User | None:

        user_id = await TokenCrud.get_access_token_payload(access_token=access_token)

        return await self.get_existing_user(user_id=user_id)

    async def abort_user_sessions(self, username: str = None, user_id: str = None) -> None:

        if not username and not user_id:
            raise exceptions.NoUserData

        user = await self.get_existing_user(username=username, user_id=user_id)

        if not user:
            raise exceptions.UserDoesNotExist

        refresh_token = await RefreshTokenDAO.find_one_or_none(Refresh_token.user_id == user.id)

        if refresh_token:
            await RefreshTokenDAO.delete(user_id=refresh_token.user_id)

        await UserDAO.update(User.id == user.id, obj_in={'is_active': False})

        return {"message": "Delete successful"}

    async def delete_user(self, username: str = None, user_id: str = None) -> None:

        if not username and not user_id:
            raise exceptions.NoUserData

        user = await self.get_existing_user(username=username, user_id=user_id)

        if not user:
            raise exceptions.UserDoesNotExist

        refresh_token = await RefreshTokenDAO.find_one_or_none(Refresh_token.user_id == user.id)

        if refresh_token:
            await RefreshTokenDAO.delete(user_id=refresh_token.user_id)

        await UserDAO.delete(or_(user_id == User.id, username == User.username))

        return {"Message": "Delete was successful"}


class TokenCrud:

    # Функция для создания access токена с указанием срока действия
    async def _create_access_token(self, data: str):

        """ Создает access токен """

        data_dict = {
            "sub": data
        }

        # Создание словаря с данными для кодирования
        to_encode = data_dict.copy()

        # Вычисление времени истечения срока действия токена
        expire = datetime.utcnow() + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})

        # Кодирование токена с использованием секретного ключа и алгоритма
        encoded_jwt = jwt.encode(
            to_encode, TOKEN_SECRET_KEY, algorithm=ALGORITHM)

        return encoded_jwt

    # Создание refresh токена

    async def _create_refresh_token(self) -> str:
        return await get_unique_id()

    async def create_tokens(self, user_id: str, response: Response, isDev: bool = False):

        # Создание access и refresh токенов на основе payload
        access_token = await self._create_access_token(user_id)
        refresh_token = await self._create_refresh_token()

        refresh_token_expires = timedelta(
            days=int(REFRESH_TOKEN_EXPIRE_DAYS))

        await RefreshTokenDAO.add(
            schemas.RefreshTokenCreate(
                user_id=user_id,
                refresh_token=refresh_token,
                expires_at=refresh_token_expires.total_seconds()
            )
        )

        if isDev:
            await self._set_cookies(response=response, access_token=access_token, refresh_token=refresh_token)

        return schemas.Token(access_token=access_token, refresh_token=refresh_token)

    async def _set_cookies(self, response: Response, access_token: str, refresh_token: str):
        response.set_cookie(
            'access_token',
            access_token,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES,
            httponly=True
        )
        response.set_cookie(
            'refresh_token',
            refresh_token,
            max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            httponly=True
        )

    async def get_access_token_payload(self, access_token: str):
        try:
            payload = jwt.decode(access_token,
                                 TOKEN_SECRET_KEY,
                                 algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            return user_id

        except jwt.ExpiredSignatureError as e:
            logger.opt(exception=e).critical("Error in delete_file")
            raise exceptions.TokenExpired

        except jwt.DecodeError as e:
            logger.opt(exception=e).critical(
                "Error in get_access_token_payload")
            raise exceptions.InvalidToken

    async def refresh_token(self, token: str, response: Response) -> schemas.Token:

        refresh_token_session, user = await self._check_refresh_token_session(token)

        access_token = await self._create_access_token(data=user.id)
        refresh_token = await self._create_refresh_token()

        refresh_token_expires = timedelta(days=int(REFRESH_TOKEN_EXPIRE_DAYS))

        await RefreshTokenDAO.update(
            Refresh_token.id == refresh_token_session.id,
            obj_in=schemas.RefreshTokenUpdate(
                refresh_token=refresh_token,
                expires_at=refresh_token_expires.total_seconds(),
                user_id=user.id,
            )
        )

        await self._set_cookies(response=response, access_token=access_token, refresh_token=refresh_token)

        return schemas.Token(access_token=access_token, refresh_token=refresh_token)

    async def _check_refresh_token_session(self, token: str):

        refresh_token_session = await RefreshTokenDAO.find_one_or_none(Refresh_token.refresh_token == token)

        if refresh_token_session is None:
            raise exceptions.InvalidToken

        if datetime.now(timezone.utc) >= refresh_token_session.created_at + timedelta(seconds=refresh_token_session.expires_at):

            await RefreshTokenDAO.delete(id=refresh_token_session.id)
            raise exceptions.TokenExpired

        user = await UserDAO.find_one_or_none(id=refresh_token_session.user_id)

        if user is None:
            raise exceptions.InvalidToken

        return refresh_token_session, user

# Определение класса для управления всеми crud-классами


class DatabaseManager:
    def __init__(self):
        self.user_crud = UserCRUD()
        self.token_crud = TokenCrud()
