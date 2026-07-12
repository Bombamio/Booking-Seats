"""Сервисный слой аутентификации.

Модуль описывает проверку учётных данных и выдачу JWT-токена.

Классы:
   - `AuthService` — аутентификация по email или телефону.

Связанные слои:
   - CRUD — в `src/crud/user.py`;
   - схемы — в `src/schemas/auth.py`.
"""

from datetime import timedelta

from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.constants import ACCESS_TOKEN_EXPIRE_MINUTES
from src.core.security import create_access_token, verify_password
from src.crud.user import user_crud
from src.models import User
from src.schemas import AuthToken
from src.services.base import BaseService


class AuthService(BaseService):
    """Сервис для аутентификации."""

    async def authenticate_user(
        self,
        session: AsyncSession,
        login: str,
        password: str,
    ) -> AuthToken:
        """Проверит email/телефон и пароль, вернёт JWT-токен доступа."""
        filters = [or_(User.email == login, User.phone == login)]
        user = await user_crud.get(session, *filters)

        if not user or not verify_password(password, user.password_hash):
            self.raise_unprocessable_entity(
                message='Неверные имя пользователя или пароль',
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={'sub': str(user.id)},
            expires_delta=access_token_expires,
        )
        return AuthToken(access_token=access_token, token_type='Bearer')
