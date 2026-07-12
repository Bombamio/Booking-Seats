"""Сервисный слой блюд.

Модуль описывает бизнес-логику управления блюдами кафе.

Классы:
   - `DishService` — список, создание, получение и обновление блюд.

Связанные слои:
   - CRUD — в `src/crud/dish.py`;
   - схемы — в `src/schemas/dish.py`.
"""

import uuid
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import CRUDDish, dish_crud
from src.models import Dish, User, UserRole
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

        if await self.exists(session, *filters):
            self.log_warning(f'Блюдо с названием {name} - уже существует.')
            self.raise_unprocessable_entity()

    async def get_multi_dishes(
        self,
        cafe_id: uuid.UUID | None,
        user: User,
        session: AsyncSession,
        show_active: bool | None,
    ) -> Sequence[Dish]:
        """Вернёт список блюд с учётом роли и фильтра по кафе.

        Проверяет существование ``cafe_id``, если он передан.
        Применяет ``is_active_filters``: USER видит только активные блюда,
        ADMIN может запросить все/активные/неактивные, MANAGER — активные
        или неактивные по ``show_active``.
        """
        filters = await self._filters_for_cafe_linked_entity(
            session=session,
            user=user,
            show_active=show_active,
            cafe_id=cafe_id,
            entity_model=Dish,
            is_active_column=Dish.is_active,
        )

        dishes = await self.get_multi(session, *filters)
        self.log_info(f'Пользователь {user.id} получил список из {len(dishes)} блюд.')
        return dishes

    async def create_dish(
        self,
        dish_create: DishCreate,
        user: User,
        session: AsyncSession,
    ) -> Dish:
        """Создаст блюдо и привяжет его к кафе из ``cafes_id``.

        Проверяет существование кафе, доступ менеджера к списку кафе
        и уникальность названия блюда.
        """
        cafes = await self._load_cafes_for_link(
            session,
            dish_create.cafes_id,
            user,
            check_manager_single=True,
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
        """Вернёт блюдо по ID с учётом роли.

        USER получает только активное блюдо.
        MANAGER дополнительно проверяется на доступ к кафе блюда.
        """
        filters = [Dish.id == dish_id]
        if user.role == UserRole.USER:
            filters.append(Dish.is_active.is_(True))

        dish: Dish = await self.get_or_raise(
            dish_crud,
            session,
            *filters,
        )

        await self.ensure_manager_cafe_list_access(
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
        """Обновит блюдо: поля, привязку к кафе и название.

        При смене ``cafes_id`` проверяет существование кафе и доступ менеджера.
        При смене ``name`` проверяет уникальность среди других блюд.
        """
        dish: Dish = await self.get_or_raise(
            dish_crud,
            session,
            Dish.id == dish_id,
        )

        relations = {}

        if dish_update.cafes_id is not None:
            relations['cafes'] = await self._load_cafes_for_link(
                session,
                dish_update.cafes_id,
                user,
                check_manager_single=True,
            )

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
