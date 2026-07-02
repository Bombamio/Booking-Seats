from datetime import timedelta
from typing import Optional

from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.constants import ACCESS_TOKEN_EXPIRE_MINUTES
from src.core.security import create_access_token, verify_password
from src.crud.user import user_crud
from src.models.user import User
from src.schemas.auth import AuthToken
from src.services.base import BaseService


class AuthService(BaseService):
    """Сервис для аутентификации."""

    async def authenticate_user(
        self,
        session: AsyncSession,
        login: str,
        password: str,
    ) -> Optional[AuthToken]:
        """Аутентификация пользователя по email/phone."""
        filters = [or_(User.email == login, User.phone == login)]
        user = await user_crud.get(session, *filters)

        if not user or not verify_password(password, user.password_hash):
            raise self.raise_unprocessable_entity(
                message='Неверные имя пользователя или пароль',
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires,
        )
        return AuthToken(access_token=access_token, token_type="Bearer")
