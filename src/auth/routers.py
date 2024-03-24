from typing import Optional

from fastapi import APIRouter, Depends, Request, Response, status

from . import schemas
from .dependencies import get_current_active_user, get_current_superuser, get_current_user
from .models import User
from .service import AuthService, UserService


auth_router = APIRouter(prefix="/auth")
user_router = APIRouter(prefix="/users")


@auth_router.post("/registration", status_code=status.HTTP_201_CREATED)
async def registration(user: schemas.UserCreate) -> schemas.UserGet:
    return await UserService.create_user(user)


# @auth_router.post("/create_accounts", status_code=status.HTTP_201_CREATED)  # noqa
# async def create_accounts(
#     superuser=Depends(get_current_superuser), default_role: str = "explorer", account_count: int = 1
# ) -> list[schemas.UserCreate]:
#     return await UserService.create_user_accounts(account_count, default_role)


@auth_router.post("/login")
async def login(response: Response, user: schemas.LoginIn) -> schemas.UserGet:
    return await AuthService.login(user.username, user.password, response)


@auth_router.post("/logout")
async def logout(request: Request, response: Response, user: User = Depends(get_current_active_user)):
    token = request.cookies.get("refresh_token")
    return await AuthService.logout(token, response, user)


@auth_router.put("/refresh_token")
async def refresh_token(response: Response, request: Request) -> dict:
    token = request.cookies.get("refresh_token")
    return await AuthService.refresh_token(response, token)


# @auth_router.delete("/abort_all_sessions")  #noqa
# async def abort_all_sessions(
#     user_id: str,
# ) -> dict:
#     return await AuthService.abort_all_sessions(user_id)


@user_router.get("/me", response_model=schemas.UserGet)
async def get_me(user: User = Depends(get_current_user)):
    return user


# @user_router.get("/get")  # noqa
# async def get_user(
#     request: Request,
#     user_id: str = None,
# ) -> schemas.UserGet:
#     token = request.cookies.get("access_token")
#     return await UserService.get_user(token=token, user_id=user_id)


@user_router.get("/get_all")
async def get_all_users(
    offset: Optional[int] = 0,
    limit: Optional[int] = 100,
    is_active: bool = True,
    user: User = Depends(get_current_active_user),
) -> list[schemas.UserGet]:
    return await UserService.get_all_users(is_active=is_active, offset=offset, limit=limit, user=user)


@user_router.patch("/set_user_role")
async def set_user_role(
    user_id: str,
    new_role: schemas.UserRole,
    superuser: User = Depends(get_current_superuser),
) -> dict:
    return await UserService.set_user_role(user_id=user_id, new_role=new_role, superuser=superuser)


@user_router.patch("/change_password")
async def change_password(
    password: schemas.ChangeUserPassword, user: User = Depends(get_current_user)
) -> dict:
    return await UserService.change_password(user, password)


@user_router.delete("/deactivate")
async def deactivate_user(user_id: str, superuser: User = Depends(get_current_superuser)) -> dict:
    return await UserService.deactivate_user_account(user_id=user_id)


# @user_router.delete("/delete")  # noqa
# async def delete_user(user_id: str, superuser: User = Depends(get_current_superuser)) -> dict:
#     return await UserService.delete_user(user_id=user_id)
