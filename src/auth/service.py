import jwt
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import or_

from . import schemas, models, exceptions, utils
from .dao import UserDAO, RefreshTokenDAO

from ..config import settings


class UserService:
    
    @classmethod
    async def create_user(cls, user: schemas.UserCreate) -> models.User:
        
        await cls.__check_if_user_exists(username=user.username)
        
        return await cls.__create_db_user(user=user)
    
    @staticmethod
    async def __create_db_user(user: schemas.UserCreate) -> models.User:
        
        hashed_password = await utils.get_hashed_password(user.password)
        
        return await UserDAO.add(
            schemas.UserCreateDB(
                **user.model_dump(),
                id=id,
                hashed_password=hashed_password
            )
        )
        
    @staticmethod
    async def __check_if_user_exists(username: str) -> None:
        
        if await UserDAO.find_all(models.User.username == username):
            raise exceptions.UserAlreadyExists

    @classmethod
    async def get_user(cls, user_id: uuid.UUID = None, token: str = None, username: str = None) -> models.User:
        
        if not user_id and not token and not username:
            raise exceptions.NoUserData
        
        if token:
            user_id = await cls._get_access_token_payload(access_token=token)
        
        return await UserDAO.find_one_or_none(or_(models.User.id == user_id, models.User.username == username))
    
    @classmethod
    async def get_all_users(cls, *filter, offset: int, limit: int, **filter_by) -> list[models.User]:

        return await UserDAO.find_all(*filter, offset=offset, limit=limit, **filter_by)
    
    @classmethod
    async def __check_if_superuser(cls, access_token: str):   
         
        user = await cls.get_user(token=access_token)
        if not user.is_superuser:
            raise exceptions.Forbidden

    @classmethod
    async def set_superuser(cls, access_token: str, user_id: str) -> dict:
        
        await cls.__check_if_superuser(access_token)
            
        return await cls.__set_superuser_db(user_id)
    
    @classmethod
    async def __set_superuser_db(cls, user_id: str) -> dict:
    
        user = await cls.get_user(user_id=user_id)     
        if not user:
            raise exceptions.UserDoesNotExist
        
        await UserDAO.update(models.User.id==user.id, obj_in={"is_superuser": not(user.is_superuser)})
        return {"Message": f"User {user_id} now has superuser status: {not(user.is_superuser)}"}
            
    @classmethod
    async def delete_user(cls, access_token: str, user_id: uuid.UUID) -> dict:
        
        await cls.__check_if_superuser(access_token)
        
        return await cls.__set_user_inactive(user_id)
        
    @classmethod
    async def __set_user_inactive(cls, user_id: uuid.UUID) -> dict:
        
        db_user = await UserDAO.find_one_or_none(id=user_id)
        if db_user is None:
            raise exceptions.UserDoesNotExist
        
        await UserDAO.update(models.User.id == user_id, obj_in={'is_active': False})
        return {"Message": f"User {user_id} was deleted successfuly"}
    
    @classmethod
    async def delete_user_from_superuser(cls, access_token: str, user_id: uuid.UUID) -> dict:
        
        await cls.__check_if_superuser(access_token)
        
        await UserDAO.delete(models.User.id == user_id)
        return {"Message": f"Superuser deleted {user_id} successfuly"}
    
    @staticmethod
    async def _get_access_token_payload(access_token: str) -> uuid.UUID:
        try:
            payload = jwt.decode(access_token,settings.TOKEN_SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")
            return user_id

        except jwt.ExpiredSignatureError as e:
            raise exceptions.TokenExpired

        except jwt.DecodeError as e:
            raise exceptions.InvalidToken
    
    
class AuthService:
    
    @classmethod
    async def create_tokens(cls, user_id: uuid.UUID) -> schemas.Token:
        access_token = await cls.__create_access_token(user_id=user_id)
        refresh_token = await cls.__create_refresh_token()

        return await cls.__create_tokens_db(user_id, access_token, refresh_token)

    @staticmethod
    async def __create_tokens_db(user_id: uuid.UUID, access_token: str, refresh_token: uuid.UUID) -> schemas.Token:

        await RefreshTokenDAO.add(
            schemas.RefreshTokenCreate(
                user_id=user_id,
                refresh_token=refresh_token,
                expires_in=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS).total_seconds()
            )
        )
        
        return schemas.Token(access_token=access_token, refresh_token=refresh_token)
    
    @staticmethod
    async def __create_access_token(user_id: uuid.UUID, **kwargs) -> str:

        to_encode = {
            "sub": str(user_id),
            "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        to_encode.update(**kwargs)
        encoded_jwt = jwt.encode(to_encode, settings.TOKEN_SECRET_KEY, algorithm=settings.ALGORITHM)

        return encoded_jwt
    
    @classmethod
    async def __create_refresh_token(cls) -> uuid.UUID:
        return uuid.uuid4()
    
    @classmethod
    async def refresh_token(cls, token: uuid.UUID) -> schemas.Token:
        
        refresh_token = await RefreshTokenDAO.find_one_or_none(models.RefreshToken.refresh_token == token)
        if refresh_token is None:
            raise exceptions.InvalidToken
        
        if datetime.now(timezone.utc) >= refresh_token.created_at + timedelta(seconds=refresh_token.expires_in):
            await RefreshTokenDAO.delete(id=refresh_token.id)
            raise exceptions.TokenExpired
        
        user = await UserDAO.find_one_or_none(id=refresh_token.user_id)
        if user is None:
            raise exceptions.InvalidToken
        
        access_token = await cls.__create_access_token(user.id)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        new_refresh_token = await cls.__create_refresh_token()
        
        await RefreshTokenDAO.update(
            models.RefreshToken.id == refresh_token.id,
            obj_in=schemas.RefreshTokenUpdate(
                refresh_token=new_refresh_token,
                expires_in=refresh_token_expires.total_seconds()
            )
        )
        
        return schemas.Token(access_token=access_token, refresh_token=new_refresh_token)
    
    @classmethod
    async def authenticate_user(cls, username: str, password: str) -> models.User:
        
        user = await UserDAO.find_one_or_none(username=username)
        if user and await utils.validate_password(password, user.hashed_password):
            return user
        
        raise exceptions.InvalidAuthenthicationCredential
    
    @classmethod
    async def logout(cls, token: uuid.UUID) -> dict:
        
        refresh_token = await RefreshTokenDAO.find_one_or_none(models.RefreshToken.refresh_token == token)
        if refresh_token:
            await RefreshTokenDAO.delete(id=refresh_token.id)
        
        return {"Message": "logout was successful"}
    
    @classmethod
    async def abort_all_sessions(cls, user_id: uuid.UUID):
        await RefreshTokenDAO.delete(models.RefreshToken.user_id == user_id)
        
        return {"Message": f"Aborting all user {user_id} sessions was successful"}

