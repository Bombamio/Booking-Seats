from typing import Any
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logger import bookingseats_logger
from src.core.security import hash_password
from src.crud.base import CRUDBase
from src.models import Cafe, User
from src.schemas import user as schema


class CRUDUser(CRUDBase):
    """CRUD функции для модели User."""

    async def duplicate_contact(
        self,
        session: AsyncSession,
        *,
        email: str | None = None,
        phone: str | None = None,
        exclude_id: UUID | None = None,
    ) -> bool:
        """Проверка занятости email и/или phone (каждое поле отдельно)."""
        clauses = []
        if email:
            clauses.append(User.email == email)
        if phone:
            clauses.append(User.phone == phone)
        if not clauses:
            return False

        filters: list[Any] = [or_(*clauses)]
        if exclude_id is not None:
            filters.append(User.id != exclude_id)
        return bool(await self.exists(session, *filters))

    async def create(
        self,
        user_create: schema.UserCreate,
        session: AsyncSession,
        **relations: Any,
    ) -> User:
        """Создание пользователя."""
        password_hash = hash_password(user_create.password)

        user_payload = user_create.model_dump(exclude={'password'})
        user_payload['password_hash'] = password_hash

        user_entity = self.model(**user_payload)

        self._set_relation(user_entity, relations)

        session.add(user_entity)
        bookingseats_logger.debug(
            f'create {self.model.__name__} id={user_entity.id}: '
            f'data={user_payload}, relations={list(relations.keys())}',
        )
        await session.commit()
        await session.refresh(user_entity)

        return user_entity

    async def update(
        self,
        user_entity: User,
        user_update: schema.UserUpdate,
        session: AsyncSession,
        **relations: Any,
    ) -> User:
        """Обновление пользователя."""
        user_update_payload = user_update.model_dump(exclude_unset=True)

        if 'password' in user_update_payload:
            user_update_payload['password_hash'] = hash_password(user_update_payload.pop('password'))

        for field, value in user_update_payload.items():
            if field in self.model_fields:
                setattr(user_entity, field, value)

        self._set_relation(user_entity, relations)

        session.add(user_entity)
        bookingseats_logger.debug(
            f'update {self.model.__name__} id={user_entity.id}: '
            f'data={user_update_payload}, relations={list(relations.keys())}',
        )
        await session.commit()
        await session.refresh(user_entity)

        return user_entity

    async def update_link_in_cafe(
        self,
        session: AsyncSession,
        new_managers: list[User],
        new_cafe: Cafe | None,
    ) -> None:
        """Закрепляем менеджера за кафе (commit делать на стороне сервиса)."""
        for manager in new_managers:
            if new_cafe:
                manager.cafe_id = new_cafe.id
            else:
                manager.cafe_id = None
            session.add(manager)

        await session.flush()


user_crud = CRUDUser(User)
