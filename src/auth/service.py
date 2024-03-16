import uuid
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Response
from sqlalchemy import or_

from ..config import settings
from ..utils import log_error_with_method_info
from . import exceptions, models, schemas, utils
from .dao import RefreshTokenDAO, UserDAO


class UserService:

    @classmethod
    async def create_user(cls, user: schemas.UserCreate) -> models.User:
        try:
            await cls.__check_if_user_exists(username=user.username)
            return await cls.__create_db_user(user=user)

        except Exception as e:
            log_error_with_method_info(e)

    @classmethod
    async def create_user_accounts(cls, account_count: int, default_role: str) -> list[models.User]:
        try:
            user_list = []
            for _ in range(account_count):
                user_account_data = await cls.__generate_user_account_data(default_role)
                user_list.append(user_account_data)
                await cls.create_user(user_account_data)
            return user_list

        except Exception as e:
            log_error_with_method_info(e)

    @staticmethod
    async def __generate_user_account_data(default_role: str) -> schemas.UserCreate:
        try:
            return schemas.UserCreate(
                username=await utils.get_random_string(10),
                password=await utils.get_random_string(10),
                role=default_role,
            )

        except Exception as e:
            log_error_with_method_info(e)

    @staticmethod
    async def __create_db_user(user: schemas.UserCreate) -> models.User:
        try:
            hashed_password = await utils.get_hashed_password(user.password)
            return await UserDAO.add(
                schemas.UserCreateDB(**user.model_dump(), hashed_password=hashed_password)
            )

        except Exception as e:
            log_error_with_method_info(e)

    @staticmethod
    async def __check_if_user_exists(username: str) -> None:
        try:
            if await UserDAO.find_all(models.User.username == username):
                raise exceptions.UserAlreadyExists

        except Exception as e:
            log_error_with_method_info(e)

    @classmethod
    async def get_user(
        cls, user_id: uuid.UUID = None, token: str = None, username: str = None
    ) -> models.User:
        try:
            if not user_id and not token and not username:
                raise exceptions.NoUserData

            if token:
                user_id = await cls._get_access_token_payload(access_token=token)
            return await UserDAO.find_one_or_none(
                or_(models.User.id == user_id, models.User.username == username)
            )

        except Exception as e:
            log_error_with_method_info(e)

    @classmethod
    async def get_all_users(cls, *filter, offset: int, limit: int, **filter_by) -> list[models.User]:
        try:
            return await UserDAO.find_all(*filter, offset=offset, limit=limit, **filter_by)

        except Exception as e:
            log_error_with_method_info(e)

    @classmethod
    async def set_superuser(cls, user_id: str) -> dict:
        try:
            return await cls.__set_superuser_db(user_id)

        except Exception as e:
            log_error_with_method_info(e)

    @classmethod
    async def set_user_role(cls, user_id: str, new_role: str) -> dict:
        try:
            return await cls.__set_user_role(user_id, new_role)

        except Exception as e:
            log_error_with_method_info(e)

    @classmethod
    async def __set_superuser_db(cls, user_id: str) -> dict:
        try:
            user = await cls.get_user(user_id=user_id)
            if not user:
                raise exceptions.UserDoesNotExist

            await UserDAO.update(models.User.id == user.id, obj_in={"is_superuser": not (user.is_superuser)})
            return {"Message": f"User {user_id} now has superuser status: {not (user.is_superuser)}"}

        except Exception as e:
            log_error_with_method_info(e)

    @classmethod
    async def __set_user_role(cls, user_id: str, new_role: str) -> dict:
        try:
            user = await cls.get_user(user_id=user_id)
            if not user:
                raise exceptions.UserDoesNotExist

            await UserDAO.update(models.User.id == user.id, obj_in={"role": new_role})
            return {"Message": f"User {user_id} now has role {new_role}"}

        except Exception as e:
            log_error_with_method_info(e)

    @classmethod
    async def change_password(cls, user: models.User, password: schemas.ChangeUserPassword) -> dict:
        try:
            await utils.validate_password(password.old_password, user.hashed_password)
            new_hashed_password = await utils.get_hashed_password(password.new_password)
            await UserDAO.update(models.User.id == user.id, obj_in={"hashed_password": new_hashed_password})
            return {"message": "Пароль был изменен успешно"}

        except Exception as e:
            log_error_with_method_info(e)

    @classmethod
    async def deactivate_user_account(cls, user_id: uuid.UUID) -> dict:
        try:
            return await cls.__set_user_inactive(user_id)

        except Exception as e:
            log_error_with_method_info(e)

    @classmethod
    async def __set_user_inactive(cls, user_id: uuid.UUID) -> dict:
        try:
            db_user = await UserDAO.find_one_or_none(id=user_id)
            if db_user is None:
                raise exceptions.UserDoesNotExist

            await UserDAO.update(models.User.id == user_id, obj_in={"is_active": False})
            return {"Message": f"User {user_id} was deleted successfuly"}

        except Exception as e:
            log_error_with_method_info(e)

    @classmethod
    async def delete_user(cls, user_id: uuid.UUID) -> dict:
        try:
            await UserDAO.delete(models.User.id == user_id)
            return {"Message": f"Superuser deleted {user_id} successfuly"}

        except Exception as e:
            log_error_with_method_info(e)

    @staticmethod
    async def _get_access_token_payload(access_token: str) -> uuid.UUID:
        try:
            access_token = access_token.split()[1]
            payload: dict = jwt.decode(
                access_token, settings.TOKEN_SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            user_id = payload.get("sub")
            return user_id

        except jwt.ExpiredSignatureError as e:
            raise exceptions.TokenExpired from e

        except jwt.DecodeError as e:
            raise exceptions.InvalidToken from e

        except Exception as e:
            log_error_with_method_info(e)


class AuthService:

    @classmethod
    async def create_tokens(cls, user_id: uuid.UUID, response: Response) -> schemas.Token:
        try:
            access_token = await cls.__create_access_token(user_id=user_id)
            refresh_token = await cls.__create_refresh_token()
            await cls.__set_tokens_in_cookie(response, access_token, refresh_token)
            return await cls.__create_tokens_db(user_id, access_token, refresh_token)

        except Exception as e:
            log_error_with_method_info(e)

    @staticmethod
    async def __set_tokens_in_cookie(response: Response, access_token: str, refresh_token: uuid.UUID) -> None:
        try:
            response.set_cookie(
                "access_token",
                access_token,
                max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                httponly=True,
                samesite="None",
                secure=True,
            )
            response.set_cookie(
                "refresh_token",
                refresh_token,
                max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 30 * 24 * 60,
                httponly=True,
                samesite="None",
                secure=True,
            )

        except Exception as e:
            log_error_with_method_info(e)

    @staticmethod
    async def __create_tokens_db(
        user_id: uuid.UUID, access_token: str, refresh_token: uuid.UUID
    ) -> schemas.Token:
        try:
            await RefreshTokenDAO.add(
                schemas.RefreshTokenCreate(
                    user_id=user_id,
                    refresh_token=refresh_token,
                    expires_in=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS).total_seconds(),
                )
            )
            return schemas.Token(access_token=access_token, refresh_token=refresh_token, token_type="Bearer")

        except Exception as e:
            log_error_with_method_info(e)

    @staticmethod
    async def __create_access_token(user_id: uuid.UUID, **kwargs) -> str:
        try:
            to_encode = {
                "sub": str(user_id),
                "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            }
            to_encode.update(**kwargs)
            encoded_jwt = jwt.encode(to_encode, settings.TOKEN_SECRET_KEY, algorithm=settings.ALGORITHM)

            return f"Bearer {encoded_jwt}"

        except Exception as e:
            log_error_with_method_info(e)

    @classmethod
    async def __create_refresh_token(cls) -> uuid.UUID:
        try:
            return uuid.uuid4()

        except Exception as e:
            log_error_with_method_info(e)

    @classmethod
    async def refresh_token(cls, response: Response, token: uuid.UUID) -> dict:
        try:
            if token is None:
                raise exceptions.Unauthorized

            refresh_token = await RefreshTokenDAO.find_one_or_none(models.RefreshToken.refresh_token == token)
            if refresh_token is None:
                raise exceptions.InvalidToken

            if datetime.now(timezone.utc) >= refresh_token.created_at + timedelta(
                seconds=refresh_token.expires_in
            ):
                await RefreshTokenDAO.delete(id=refresh_token.id)
                await cls.__delete_tokens_from_cookie(response)
                raise exceptions.TokenExpired

            user = await UserDAO.find_one_or_none(id=refresh_token.user_id)
            if user is None:
                raise exceptions.InvalidToken

            access_token = await cls.__create_access_token(user.id)
            refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
            new_refresh_token = await cls.__create_refresh_token()

            await cls.__set_tokens_in_cookie(response, access_token, new_refresh_token)
            await RefreshTokenDAO.update(
                models.RefreshToken.id == refresh_token.id,
                obj_in=schemas.RefreshTokenUpdate(
                    refresh_token=new_refresh_token, expires_in=refresh_token_expires.total_seconds()
                ),
            )
            return {"message": "Tokens were refreshed successfully"}

        except Exception as e:
            log_error_with_method_info(e)

    @classmethod
    async def authenticate_user(cls, username: str, password: str, response: Response) -> models.User:
        try:
            user = await UserDAO.find_one_or_none(username=username)

            if user and await utils.validate_password(password, user.hashed_password):
                await cls.create_tokens(user.id, response)
                return user

            raise exceptions.InvalidAuthenthicationCredential

        except Exception as e:
            log_error_with_method_info(e)

    @classmethod
    async def logout(cls, token: uuid.UUID, response: Response) -> dict:
        try:
            if token is None:
                raise exceptions.Unauthorized

            await cls.__delete_tokens_db(token)
            await cls.__delete_tokens_from_cookie(response)

            return {"Message": "logout was successful"}

        except Exception as e:
            log_error_with_method_info(e)

    @staticmethod
    async def __delete_tokens_from_cookie(response: Response):
        try:
            response.set_cookie(
                "access_token", "access_token", max_age=0, httponly=True, samesite="None", secure=True
            )
            response.set_cookie(
                "refresh_token", "refresh_token", max_age=0, httponly=True, samesite="None", secure=True
            )

        except Exception as e:
            log_error_with_method_info(e)

    @staticmethod
    async def __delete_tokens_db(token: uuid.UUID):
        try:
            refresh_token = await RefreshTokenDAO.find_one_or_none(models.RefreshToken.refresh_token == token)
            if refresh_token:
                await RefreshTokenDAO.delete(id=refresh_token.id)

        except Exception as e:
            log_error_with_method_info(e)

    @classmethod
    async def abort_all_sessions(cls, user_id: uuid.UUID):
        try:
            await RefreshTokenDAO.delete(models.RefreshToken.user_id == user_id)
            return {"Message": f"Aborting all user {user_id} sessions was successful"}

        except Exception as e:
            log_error_with_method_info(e)
