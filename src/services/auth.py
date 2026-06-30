from typing import Optional

from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import verify_password
from src.crud.user import user_crud
from src.models.user import User
from src.schemas.auth import AuthToken
from src.services.base import BaseService


class AuthService(BaseService):
    """Сервис для аутентификации."""

    @staticmethod
    def authenticate_user(
        session: AsyncSession,
        login: str,
        password: str,
    ) -> Optional[AuthToken]:
        """Аутентификация пользователя по email/phone."""
        filters = [or_(User.email == login, User.phone == login)]
        user = user_crud.get(session, *filters)
        if not user:
            verify_password(password, user.password_hash)
            return False
        if not verify_password(password, user.password_hash):
            return False
        return user
