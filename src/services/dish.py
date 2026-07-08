import uuid
from typing import Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import CRUDDish, cafe_crud, dish_crud
from src.models import Cafe, Dish, User, UserRole
from src.schemas import DishCreate, DishUpdate
from src.services.base import BaseService


class DishService(CRUDDish, BaseService):
    """Обработка операций с блюдами."""

    async def _ensure_name_unique(
        self,
        name: str,
        session: AsyncSession,
        exclude_id: uuid.UUID | None = None,
    ) -> None:
        """Проверит уникальность названия блюда."""
        filters = [Dish.name == name]
        if exclude_id is not None:
            filters.append(Dish.id != exclude_id)

        if await self.exists(
            session=session,
            *filters,
        ):
            self.log_warning(f'Блюдо с назанием {name} - уже существует.')
            self.raise_unprocessable_entity()

    async def get_multi_dishes(
        self,
        cafe_id: Optional[uuid.UUID],
        user: User,
        session: AsyncSession,
        show_active: Optional[bool],
    ) -> Sequence[Dish]:
        """Вернет список блюд с учётом роли пользователя.

        По умолчанию показывает:

        * для пользователя - только активные блюда (всегда, в не зависимости
        от значения параметра).
        * для администратора - все блюда (и активные и не активные)
        * для менеджера - активные блюда
        """
        filters = []

        if cafe_id is not None:
            filters.append(Dish.cafes.any(Cafe.id == cafe_id))

        if user.role == UserRole.USER or show_active or user.role == UserRole.MANAGER and show_active is None:
            filters.append(Dish.is_active.is_(True))

        elif show_active is False and user.role == UserRole.MANAGER and cafe_id is not None:
            filters.append(
                Dish.cafes.any(Cafe.managers.any(User.id == user.id)),
            )

        elif user.role != UserRole.USER and show_active is not None:
            filters.append(Dish.is_active.is_(show_active))

        dishes = await self.get_multi(session, *filters)
        self.log_info(f'Пользователь {user.id} получил список из {len(dishes)} блюд.')
        return dishes

    async def create_dish(
        self,
        dish_create: DishCreate,
        user: User,
        session: AsyncSession,
    ) -> Dish:
        """Вернёт новое блюдо.

        Только для администраторов и менеджеров.
        """
        cafes = await cafe_crud.get_multi(
            session,
            Cafe.id.in_(dish_create.cafes_id),
        )

        await self.ensure_cafes_len(
            cafes=cafes,
            cafes_id=dish_create.cafes_id,
        )
        await self.ensure_manajer_cafe_list_access(
            user=user,
            cafes_id=dish_create.cafes_id,
            check_len=True,
        )
        await self._ensure_name_unique(
            name=dish_create.name,
            session=session,
        )

        result = await self.create(
            dish_create,
            session,
            cafes=cafes,
        )

        self.log_info(f'Пользователь {user.id} создал блюдо {dish_create.name}.')

        return result

    async def get_dish_by_id(
        self,
        dish_id: uuid.UUID,
        user: User,
        session: AsyncSession,
    ) -> Dish:
        """Получение информации о блюде по его ID.

        * для администраторов и менеджеров - все блюда
        * для пользователей - только активные.
        """
        filters = [Dish.id == dish_id]
        if user.role == UserRole.USER:
            filters.append(Dish.is_active.is_(True))

        dish: Dish = await self.get_or_raise(
            dish_crud,
            session,
            *filters,
        )

        await self.ensure_manajer_cafe_list_access(
            user=user,
            cafes_id=[cafe.id for cafe in dish.cafes],
        )

        self.log_info(f'Пользователь {user.id} получил информацию о блюде {dish_id}.')

        return dish

    async def update_dish(
        self,
        dish_id: uuid.UUID,
        dish_update: DishUpdate,
        user: User,
        session: AsyncSession,
    ) -> Dish:
        """Обновление информации о блюде по его ID.

        Только для администраторов и менеджеров.
        """
        dish: Dish = await self.get_or_raise(
            dish_crud,
            session,
            Dish.id == dish_id,
        )

        relations = {}

        if dish_update.cafes_id is not None:
            cafes = await cafe_crud.get_multi(
                session,
                Cafe.id.in_(dish_update.cafes_id),
            )

            await self.ensure_cafes_len(
                cafes=cafes,
                cafes_id=dish_update.cafes_id,
            )

            if user.role.MANAGER:
                await self.ensure_manajer_cafe_list_access(
                    user=user,
                    cafes_id=dish_update.cafes_id,
                    check_len=True,
                )

            relations['cafes'] = cafes

        if dish_update.name is not None:
            await self._ensure_name_unique(
                name=dish_update.name,
                session=session,
                exclude_id=dish_id,
            )

        result = await self.update(
            db_entity=dish,
            update_data=dish_update,
            session=session,
            **relations,
        )

        self.log_info(f'Пользователь {user.id} изменил информацию о блюде {dish_id}.')

        return result


dish_service = DishService(Dish)
