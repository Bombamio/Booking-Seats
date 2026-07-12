"""Сервисный слой пользователей.

Модуль описывает бизнес-логику управления учётными записями.

Классы:
   - `UserService` — создание, список, получение и обновление пользователей.

Связанные слои:
   - CRUD — в `src/crud/user.py`;
   - схемы — в `src/schemas/user.py`.
"""

from typing import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import CRUDUser, user_crud
from src.models import User, UserRole
from src.schemas import user as schema
from src.services.base import BaseService


class UserService(CRUDUser, BaseService):
    """Обработка операций с пользователями."""

    def _check_role_change(
        self,
        user_in: schema.UserUpdate,
        *,
        current_user: User,
        target_user_id: UUID,
    ) -> None:
        """Только ADMIN может менять чужую роль; свою — никто."""
        if 'role' not in user_in.model_fields_set:
            return
        if current_user.role != UserRole.ADMIN or target_user_id == current_user.id:
            self.raise_forbidden('Доступ запрещен')

    async def create_user(
        self,
        session: AsyncSession,
        user_in: schema.UserCreate,
        current_user: User | None = None,
    ) -> User:
        """Создание нового пользователя."""
        if current_user is not None and current_user.role not in (
            UserRole.ADMIN,
            UserRole.MANAGER,
        ):
            self.raise_forbidden('Доступ запрещен')
        if await user_crud.duplicate_contact(
            session,
            email=user_in.email,
            phone=user_in.phone,
        ):
            self.raise_unprocessable_entity('Пользователь с таким email/phone уже существует')
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

        if (
            current_user.role == UserRole.MANAGER
            and user_in.is_active is not None
            and user_in.is_active is False
        ):
            self.raise_forbidden('Доступ запрещен')

        user = await self.get(session, User.id == user_id)
        if not user:
            self.raise_not_found()

        self._check_role_change(user_in, current_user=current_user, target_user_id=user_id)

        update_data = user_in.model_dump(exclude_unset=True)
        check_email = (
            update_data['email'] if 'email' in update_data and update_data['email'] != user.email else None
        )
        check_phone = (
            update_data['phone'] if 'phone' in update_data and update_data['phone'] != user.phone else None
        )
        if check_email or check_phone:
            if await user_crud.duplicate_contact(
                session,
                email=check_email,
                phone=check_phone,
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
        if (
            current_user.role == UserRole.USER
            and user_in.is_active is not None
            and user_in.is_active is False
        ):
            self.raise_forbidden('Доступ запрещен')
        self._check_role_change(
            user_in,
            current_user=current_user,
            target_user_id=current_user.id,
        )
        return await self.update(current_user, user_in, session)


user_service = UserService(User)
