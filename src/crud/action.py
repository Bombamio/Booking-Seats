import uuid
from typing import Any, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import Select

from src.crud.base import CRUDBase
from src.models import Action
from src.schemas import ActionCreate, ActionUpdate


class CRUDAction(CRUDBase):
    """CRUD функции для модели Action."""

    def _stmt_with_cafes(self) -> Select[tuple[Action]]:
        """Соберёт запрос с предзагрузкой связанных кафе."""
        return select(self.model).options(selectinload(self.model.cafes))

    async def _reload_with_cafes(
        self,
        session: AsyncSession,
        action_id: uuid.UUID,
    ) -> Action:
        """Перечитает акцию из БД с предзагруженными кафе."""
        result = await session.execute(
            self._stmt_with_cafes().where(self.model.id == action_id),
        )
        return result.scalars().one()

    async def get(
        self,
        session: AsyncSession,
        *filters: Any,
    ) -> Action | None:
        """Вернёт акцию с предзагруженными кафе."""
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
    ) -> Sequence[Action]:
        """Получение списка акций с фильтрацией."""
        stmt = self._stmt_with_cafes()
        if filters:
            stmt = stmt.where(*filters)
            self._check_filters(*filters)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def create(
        self,
        create_data: ActionCreate,
        session: AsyncSession,
        **relations: Any,
    ) -> Action:
        """Создание акции с привязкой к кафе."""
        action = await super().create(create_data=create_data, session=session, **relations)
        return await self._reload_with_cafes(session, action.id)

    async def update(
        self,
        db_entity: Action,
        update_data: ActionUpdate,
        session: AsyncSession,
        **relations: Any,
    ) -> Action:
        """Обновление акции, включая связи с кафе."""
        action = await super().update(db_entity, update_data, session, **relations)
        return await self._reload_with_cafes(session, action.id)


action_crud = CRUDAction(Action)
