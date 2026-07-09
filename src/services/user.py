from typing import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import CRUDUser, user_crud
from src.models import User, UserRole
from src.schemas import user as schema
from src.services.base import BaseService


class UserService(CRUDUser, BaseService):
    """Обработка операций с пользователями."""

    async def create_user(
        self,
        session: AsyncSession,
        user_in: schema.UserCreate,
    ) -> User:
        """Создание нового пользователя."""
        if await user_crud.duplicate_login(session, login=user_in.email or user_in.phone):
            raise ValueError('Пользователь с таким email/phone уже существует')
        return await self.create(user_in, session)

    async def get_user(
        self,
        session: AsyncSession,
        user_id: UUID,
        current_user: User,
    ) -> User:
        """Получение пользователя по ID."""
        if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
            self.raise_forbidden('Доступ запрещен')
        user = await self.get(session, User.id == user_id)
        if not user:
            self.raise_not_found()
        return user

    async def get_users_list(
        self,
        session: AsyncSession,
        current_user: User,
    ) -> Sequence[User]:
        """Получение списка пользователей."""
        if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
            self.raise_forbidden('Доступ запрещен')
        return await self.get_multi(session)

    async def update_user(
        self,
        session: AsyncSession,
        user_id: UUID,
        user_in: schema.UserUpdate,
        current_user: User,
    ) -> User:
        """Обновление информации о пользователе."""
        if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
            self.raise_forbidden('Доступ запрещен')

        user = await self.get(session, User.id == user_id)
        if not user:
            self.raise_not_found()

        update_data = user_in.model_dump(exclude_unset=True)
        login = update_data.get('email') or update_data.get('phone')
        if login and login != user.email and login != user.phone:
            if await user_crud.duplicate_login(
                session,
                login,
                exclude_id=user_id,
            ):
                self.raise_unprocessable_entity('Пользователь с таким email/phone уже существует')

        return await self.update(user, user_in, session)

    async def get_me(
        self,
        session: AsyncSession,
        current_user: User,
    ) -> User:
        """Получение информации о текущем пользователе."""
        return current_user

    async def update_me(
        self,
        session: AsyncSession,
        user_in: schema.UserUpdate,
        current_user: User,
    ) -> User:
        """Обновление информации о текущем пользователе."""
        return await self.update(current_user, user_in, session)


user_service = UserService(User)
