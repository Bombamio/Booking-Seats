import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import Select

from src.crud.base import CRUDBase
from src.models import Dish
from src.schemas import DishCreate, DishUpdate


class CRUDDish(CRUDBase):
    """CRUD функции для модели Dish."""

    def _stmt_with_cafes(self) -> Select[tuple[Dish]]:
        """Соберёт запрос с предзагрузкой связанных кафе."""
        return select(self.model).options(selectinload(self.model.cafes))

    async def get(
        self,
        session: AsyncSession,
        *filters: Any,
    ) -> Dish | None:
        """Вернёт блюдо с предзагруженными кафе."""
        stmt = self._stmt_with_cafes()
        if filters:
            stmt = stmt.where(*filters)
            self._check_filters(*filters)
        result = await session.execute(stmt)
        return result.scalars().first()

    async def get_multi(
        self,
        session: AsyncSession,
        *filters: Any,
    ) -> list[Dish]:
        """Вернёт список блюд с предзагруженными кафе."""
        stmt = self._stmt_with_cafes()
        if filters:
            stmt = stmt.where(*filters)
            self._check_filters(*filters)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def _reload_with_cafes(
        self,
        session: AsyncSession,
        dish_id: uuid.UUID,
    ) -> Dish:
        """Перечитает блюдо из БД с предзагруженными кафе."""
        result = await session.execute(
            self._stmt_with_cafes().where(self.model.id == dish_id),
        )
        return result.scalars().one()

    async def create(
        self,
        create_data: DishCreate,
        session: AsyncSession,
        **relations: Any,
    ) -> Dish:
        """Создаст блюдо и вернёт его с предзагруженными кафе."""
        dish = await super().create(create_data, session, **relations)
        return await self._reload_with_cafes(session, dish.id)

    async def update(
        self,
        db_entity: Dish,
        update_data: DishUpdate,
        session: AsyncSession,
        **relations: Any,
    ) -> Dish:
        """Обновит блюдо и вернёт его с предзагруженными кафе."""
        dish = await super().update(db_entity, update_data, session, **relations)
        return await self._reload_with_cafes(session, dish.id)


dish_crud = CRUDDish(Dish)
