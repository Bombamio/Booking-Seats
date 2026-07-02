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
        obj_in: schema.UserCreate,
        session: AsyncSession,
        **relations: Any,
    ) -> User:
        """Создание пользователя."""
        if await self.duplicate_login(
            session, login=obj_in.email or obj_in.phone,
        ):
            raise ValueError('Пользователь с таким email/phone уже существует')
        password_hash = hash_password(obj_in.password)

        obj_data = obj_in.model_dump(exclude={'password'})
        obj_data['password_hash'] = password_hash

        db_obj = self.model(**obj_data)

        for attr, value in relations.items():
            if attr not in self.relationships:
                raise ValueError(
                    f'{attr} is not a relationships of {self.model.__name__}',
                )
            setattr(db_obj, attr, value)

        session.add(db_obj)
        bookingseats_logger.debug(
            f'create {self.model.__name__} id={db_obj.id}: '
            f'data={obj_data}, relations={list(relations.keys())}',
        )
        await session.commit()
        await session.refresh(db_obj)

        return db_obj

    async def update(
        self,
        db_obj: User,
        obj_in: schema.UserUpdate,
        session: AsyncSession,
        **relations: Any,
    ) -> User:
        """Обновление пользователя."""
        update_data = obj_in.model_dump(exclude_unset=True)

        if 'password' in update_data:
            update_data['password_hash'] = hash_password(
                update_data.pop('password'))

        for field, value in update_data.items():
            if field in self.model_fields:
                setattr(db_obj, field, value)

        for attr, value in relations.items():
            if attr not in self.relationships:
                raise ValueError(
                    f'{attr} is not a relationships of {self.model.__name__}',
                )
            setattr(db_obj, attr, value)

        session.add(db_obj)
        bookingseats_logger.debug(
            f'update {self.model.__name__} id={db_obj.id}: '
            f'data={update_data}, relations={list(relations.keys())}',
        )
        await session.commit()
        await session.refresh(db_obj)

        return db_obj

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
