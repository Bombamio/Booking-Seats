import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_session
from src.crud import cafe_crud, user_crud
from src.models import Cafe, User, UserRole
from src.schemas import CafeCreate

SessionDep = Annotated[AsyncSession, Depends(get_session)]


class CafeService:
    """Сервис для работы бизнес логики кафе."""

    def __init__(
            self,
            session: AsyncSession,
        ):
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
            cafe_in,
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
            show_active: bool,
    ) -> list[Cafe]:
        """Метод возвращает список кафе, в зависимости от роли пользователя."""
        if user.role == UserRole.USER:
            return await cafe_crud.get_multi_with_managers(
                self.session,
                Cafe.is_active.is_(True),
            )
        return await cafe_crud.get_multi_with_managers(
            self.session,
            Cafe.is_active.is_(show_active),
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
                Cafe.id==cafe_id,
                Cafe.is_active.is_(True),
            )
        else:
            cafe = await cafe_crud.get_with_managers(
                self.session,
                Cafe.id==cafe_id,
            )

        if not cafe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Кафе с id:{cafe_id} не найдено',
            )

        return cafe

    async def update_cafe(
            self,
            cafe_in: CafeCreate,
            cafe_id: uuid.UUID,
    ) -> Cafe:
        """Обновление информации о кафе по его ID."""
        await self._validate_unique_cafe_and_address(
            name=cafe_in.name,
            address=cafe_in.address,
            is_active=True,
        )

        managers_objs = await self._validate_managers(
            managers=cafe_in.managers_id,
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

        id_exist_managers = set(manager.id for manager in cafe_old_db.managers)
        new_managers = set(cafe_in.managers_id).difference(id_exist_managers)
        unset_managers = set(id_exist_managers).difference(cafe_in.managers_id)

        new_managers_obj = []
        unset_managers_obj = []

        for manager in managers_objs:
            if manager.id in new_managers:
                new_managers_obj.append(manager)

        for manager in cafe_old_db.managers:
            if manager.id in unset_managers:
                unset_managers_obj.append(manager)

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
            cafe_old_db,
            cafe_in,
            session=self.session,
        )

        await self.session.commit()
        await self.session.refresh(update_cafe, attribute_names=['managers'])

        return update_cafe

    async def _validate_managers(
            self,
            managers: list[uuid.UUID],
        ) -> list[User]:

        managers_objs = await user_crud.get_multi(
            self.session,
            User.id.in_(managers),
        )

        id_exist_managers = {manager.id for manager in managers_objs}
        missing_ids = set(managers).difference(id_exist_managers)

        if missing_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Пользователи: {missing_ids} не найдены',
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
                    detail=(
                        f'Пользователь: {manager.username} '
                        'уже закреплен за кафе'
                    ),
                )

        return managers_objs

    async def _validate_unique_cafe_and_address(
            self,
            name: str,
            address: str,
            is_active: bool) -> None:
        if await cafe_crud.exists(
            self.session,
            Cafe.name == name,
            Cafe.address == address,
            Cafe.is_active.is_(is_active),
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "На данном адресе уже существует кафе с таким названием."
                ),
            )


def get_cafe_service(session: SessionDep) -> CafeService:
    """Функция для получения зависимости для CafeService."""
    return CafeService(session)
