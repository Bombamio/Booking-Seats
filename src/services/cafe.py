"""Сервисный слой кафе.

Модуль описывает бизнес-логику управления кафе и привязкой менеджеров.

Классы:
   - `CafeService` — создание, список, получение и обновление кафе.

Связанные слои:
   - CRUD — в `src/crud/cafe.py`;
   - схемы — в `src/schemas/cafe.py`.
"""

import uuid
from typing import Annotated, Sequence

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_session
from src.core.exceptions import BookingSeatsAppError
from src.crud import cafe_crud, user_crud
from src.models import Cafe, User, UserRole
from src.schemas import CafeCreate, CafeUpdate
from src.services.base import BaseService, is_active_filters

SessionDep = Annotated[AsyncSession, Depends(get_session)]


class CafeService(BaseService):
    """Сервис для работы бизнес логики кафе."""

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        """Сохранит сессию БД для операций сервиса."""
        self.session = session

    async def create_cafe(
        self,
        cafe_in: CafeCreate,
    ) -> Cafe:
        """Метод проверяет все парамерты и создает новое кафе."""
        await self._validate_unique_cafe_and_address(
            name=cafe_in.name,
            address=cafe_in.address,
            is_active=True,
        )

        managers_objs = await self._validate_managers(
            managers=cafe_in.managers_id,
        )

        new_cafe = await cafe_crud.create_cafe(
            cafe_create=cafe_in,
            session=self.session,
        )

        await user_crud.update_link_in_cafe(
            self.session,
            managers_objs,
            new_cafe,
        )

        await self.session.commit()
        await self.session.refresh(new_cafe, attribute_names=['managers'])

        return new_cafe

    async def get_cafes(
        self,
        user: User,
        show_active: bool | None,
    ) -> Sequence[Cafe]:
        """Метод возвращает список кафе, в зависимости от роли пользователя."""
        filters = is_active_filters(user, show_active, Cafe.is_active)
        return await cafe_crud.get_multi_with_managers(
            self.session,
            *filters,
        )

    async def get_cafe(
        self,
        cafe_id: uuid.UUID,
        user: User,
    ) -> Cafe:
        """Получение информации о кафе по его ID."""
        if user.role == UserRole.USER:
            cafe = await cafe_crud.get_with_managers(
                self.session,
                Cafe.id == cafe_id,
                Cafe.is_active.is_(True),
            )
        else:
            cafe = await cafe_crud.get_with_managers(
                self.session,
                Cafe.id == cafe_id,
            )

        if not cafe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Кафе с id:{cafe_id} не найдено',
            )

        return cafe

    async def update_cafe(
        self,
        cafe_id: uuid.UUID,
        cafe_in: CafeUpdate,
        current_user: User,
    ) -> Cafe:
        """Обновление информации о кафе по его ID."""
        if (
            current_user.role == UserRole.MANAGER
            and cafe_in.is_active is not None
            and cafe_in.is_active is False
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Доступ запрещен',
            )

        cafe_old_db = await cafe_crud.get_with_managers(
            self.session,
            Cafe.id == cafe_id,
        )
        if not cafe_old_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Кафе с id:{cafe_id} не найдено',
            )

        await self._validate_unique_cafe_and_address(
            name=cafe_in.name or cafe_old_db.name,
            address=cafe_in.address or cafe_old_db.address,
            is_active=(cafe_in.is_active if cafe_in.is_active is not None else cafe_old_db.is_active),
            exclude_id=cafe_id,
        )

        if cafe_in.managers_id is not None:
            managers_objs = await self._validate_managers(
                managers=cafe_in.managers_id,
            )
            id_exist_managers = {manager.id for manager in cafe_old_db.managers}
            new_managers = set(cafe_in.managers_id).difference(id_exist_managers)
            unset_managers = id_exist_managers.difference(cafe_in.managers_id)

            new_managers_obj = [manager for manager in managers_objs if manager.id in new_managers]
            unset_managers_obj = [manager for manager in cafe_old_db.managers if manager.id in unset_managers]

            await user_crud.update_link_in_cafe(
                self.session,
                new_managers_obj,
                cafe_old_db,
            )
            await user_crud.update_link_in_cafe(
                self.session,
                unset_managers_obj,
                None,
            )

        update_cafe = await cafe_crud.update_cafe(
            cafe_entity=cafe_old_db,
            cafe_update=cafe_in,
            session=self.session,
        )

        await self.session.commit()
        await self.session.refresh(update_cafe, attribute_names=['managers'])

        return update_cafe

    async def _validate_managers(
        self,
        managers: list[uuid.UUID],
    ) -> list[User]:
        """Проверит существование менеджеров и валидность их роли."""
        if not managers:
            return []

        await self.ensure_ids_exist(user_crud, self.session, managers)

        managers_objs = await user_crud.get_multi(
            self.session,
            User.id.in_(managers),
        )

        for manager in managers_objs:
            if manager.role != UserRole.MANAGER:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'Пользователь: {manager.username} не менеджер',
                )

            if manager.cafe_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=(f'Пользователь: {manager.username} уже закреплен за кафе'),
                )

        return managers_objs

    async def _validate_unique_cafe_and_address(
        self,
        name: str,
        address: str,
        is_active: bool,
        exclude_id: uuid.UUID | None = None,
    ) -> None:
        """Проверит, что активное кафе с таким именем и адресом отсутствует."""
        filters = [
            Cafe.name == name,
            Cafe.address == address,
            Cafe.is_active.is_(is_active),
        ]
        if exclude_id is not None:
            filters.append(Cafe.id != exclude_id)

        if await cafe_crud.exists(
            self.session,
            *filters,
        ):
            raise BookingSeatsAppError(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                'На данном адресе уже существует кафе с таким названием.',
            )


def get_cafe_service(session: SessionDep) -> CafeService:
    """Функция для получения зависимости для CafeService."""
    return CafeService(session)
