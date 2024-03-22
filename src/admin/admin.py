import uuid
from datetime import datetime, timedelta

import jwt
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse

from src.auth.dependencies import get_current_user
from src.auth.service import AuthService
from src.config import settings
from src.utils import log_error_with_method_info


async def create_access_token(user_id: uuid.UUID, **kwargs) -> str:
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


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]

        user = await AuthService.authenticate_user(username, password)
        if user:
            access_token = await create_access_token(user.id)
            request.session.update({"token": access_token})
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return RedirectResponse("/admin/login", status_code=302)

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        if not token:
            return RedirectResponse("/admin/login", status_code=302)
        token = token.split()[1]
        user = await get_current_user(token)
        if not user:
            return RedirectResponse("/admin/login", status_code=302)
        return True


authentication_backend = AdminAuth(secret_key=settings.TOKEN_SECRET_KEY)
