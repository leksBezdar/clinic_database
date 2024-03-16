from fastapi import Depends

from ..auth.dependencies import get_current_user
from ..auth.models import User
from ..auth.schemas import UserRole
from . import exceptions


def get_current_therapist(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role == UserRole.therapist.value:
        return current_user

    raise exceptions.Forbidden
