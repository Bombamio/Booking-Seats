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

    def _ensure_staff(self, user: User) -> None:
        """Разрешит операцию только ADMIN и MANAGER."""
        if user.role not in (UserRole.ADMIN, UserRole.MANAGER):
            self.raise_forbidden('Доступ запрещен')

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

    async def _ensure_unique_contacts(
        self,
        session: AsyncSession,
        *,
        email: str | None,
        phone: str | None,
        exclude_id: UUID | None = None,
    ) -> None:
        """Проверит уникальность email и телефона среди пользователей."""
        if not email and not phone:
            return
        if await user_crud.duplicate_contact(
            session,
            email=email,
            phone=phone,
            exclude_id=exclude_id,
        ):
            self.raise_unprocessable_entity('Пользователь с таким email/phone уже существует')

    async def create_user(
        self,
        session: AsyncSession,
        user_in: schema.UserCreate,
        current_user: User | None = None,
    ) -> User:
        """Создаст пользователя с проверкой прав и уникальности контактов."""
        if current_user is not None:
            self._ensure_staff(current_user)
        await self._ensure_unique_contacts(
            session,
            email=user_in.email,
            phone=user_in.phone,
        )
        return await self.create(user_in, session)

    async def get_user(
        self,
        session: AsyncSession,
        user_id: UUID,
        current_user: User,
    ) -> User:
        """Вернёт пользователя по ID (только для ADMIN и MANAGER)."""
        self._ensure_staff(current_user)
        return await self.get_or_raise(self, session, User.id == user_id)

    async def get_users_list(
        self,
        session: AsyncSession,
        current_user: User,
    ) -> Sequence[User]:
        """Вернёт список пользователей (только для ADMIN и MANAGER)."""
        self._ensure_staff(current_user)
        return await self.get_multi(session)

    async def update_user(
        self,
        session: AsyncSession,
        user_id: UUID,
        user_in: schema.UserUpdate,
        current_user: User,
    ) -> User:
        """Обновит пользователя с проверкой прав, роли и уникальности контактов."""
        self._ensure_staff(current_user)

        if (
            current_user.role == UserRole.MANAGER
            and user_in.is_active is not None
            and user_in.is_active is False
        ):
            self.raise_forbidden('Доступ запрещен')

        user = await self.get_or_raise(self, session, User.id == user_id)
        self._check_role_change(user_in, current_user=current_user, target_user_id=user_id)

        update_data = user_in.model_dump(exclude_unset=True)
        check_email = (
            update_data['email'] if 'email' in update_data and update_data['email'] != user.email else None
        )
        check_phone = (
            update_data['phone'] if 'phone' in update_data and update_data['phone'] != user.phone else None
        )
        await self._ensure_unique_contacts(
            session,
            email=check_email,
            phone=check_phone,
            exclude_id=user_id,
        )

        return await self.update(user, user_in, session)

    async def get_me(
        self,
        session: AsyncSession,
        current_user: User,
    ) -> User:
        """Вернёт текущего авторизованного пользователя."""
        return current_user

    async def update_me(
        self,
        session: AsyncSession,
        user_in: schema.UserUpdate,
        current_user: User,
    ) -> User:
        """Обновит профиль текущего пользователя."""
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
