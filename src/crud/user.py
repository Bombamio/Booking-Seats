from typing import Any

from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logger import bookingseats_logger
from src.core.security import hash_password
from src.crud.base import CRUDBase
from src.models import Cafe, User
from src.schemas import user as schema


class CRUDUser(CRUDBase):
    """CRUD функции для модели User."""

    async def duplicate_login(
        self,
        session: AsyncSession,
        login: str,
    ) -> bool:
        """Проверка, есть ли такой логин в БД."""
        filters = [or_(User.email == login, User.phone == login)]
        return await self.exists(session, *filters)

    async def create(
        self,
        user_create: schema.UserCreate,
        session: AsyncSession,
        **relations: Any,
    ) -> User:
        """Создание пользователя."""
        if await self.duplicate_login(
            session,
            login=user_create.email or user_create.phone,
        ):
            raise ValueError('Пользователь с таким email/phone уже существует')
        password_hash = hash_password(user_create.password)

        user_payload = user_create.model_dump(exclude={'password'})
        user_payload['password_hash'] = password_hash

        user_entity = self.model(**user_payload)

        for attr, value in relations.items():
            if attr not in self.relationships:
                raise ValueError(
                    f'{attr} is not a relationships of {self.model.__name__}',
                )
            setattr(user_entity, attr, value)

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

        for attr, value in relations.items():
            if attr not in self.relationships:
                raise ValueError(
                    f'{attr} is not a relationships of {self.model.__name__}',
                )
            setattr(user_entity, attr, value)

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
