from typing import Optional
from fastapi import APIRouter, Depends, Request, Response, status

from . import schemas

from .dependencies import get_current_superuser
from .models import User
from .service import UserService, AuthService

from ..config import settings

auth_router = APIRouter(prefix="/auth")
user_router = APIRouter(prefix="/users")


@auth_router.post("/registration", status_code=status.HTTP_201_CREATED)
async def registration(
    user: schemas.UserCreate
) -> schemas.UserGet:
    return await UserService.create_user(user)


@auth_router.post("/login")
async def login(
    response: Response,
    user: schemas.LoginIn
) -> schemas.LoginResponse:
    user = await AuthService.authenticate_user(user.username, user.password)
    tokens = await AuthService.create_tokens(user.id, response)

    return {"user": user, "tokens": tokens}


@auth_router.post("/logout")
async def logout(
    request: Request,
    response: Response
):
    token = request.cookies.get("refresh_token")
    return await AuthService.logout(token, response)


@auth_router.put("/refresh_token")
async def refresh_token(
    response: Response,
    request: Request
) -> schemas.Token:
    token = request.cookies.get("refresh_token")
    return await AuthService.refresh_token(response, token)


@auth_router.delete("/abort_all_sessions")
async def abort_all_sessions(
    user_id: str, 
) -> dict:
    return await AuthService.abort_all_sessions(user_id)


@user_router.get("/get_user")
async def get_user(
    request: Request,
    user_id: str = None,
) -> schemas.UserGet:
    token = request.cookies.get("access_token")
    return await UserService.get_user(token=token, user_id=user_id)

@user_router.get("/get_all_users")
async def get_all_users(
    offset: Optional[int] = 0,
    limit: Optional[int] = 100,
    is_active: bool = True,
) -> list[schemas.UserGet]:
    return await UserService.get_all_users(is_active=is_active, offset=offset, limit=limit)

@user_router.patch("/set_superuser")
async def set_superuser(
    user_id: str,    
    superuser: User = Depends(get_current_superuser),
) -> dict:
    return await UserService.set_superuser(user_id=user_id)

@user_router.delete("/delete_user")
async def delete_user(
    user_id: str,
    superuser: User = Depends(get_current_superuser)
) -> dict:
    return await UserService.delete_user(user_id=user_id)

@user_router.delete("/delete_user_from_superuser")
async def delete_user_from_superuser(
    user_id: str,
    superuser: User = Depends(get_current_superuser)
) -> dict:
    return await UserService.delete_user_from_superuser(user_id=user_id)