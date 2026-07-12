"""CRUD-слой временных слотов.

Модуль описывает операции чтения и записи для модели `Slot`.

Классы:
   - `CRUDSlot` — выборка с кафе, проверка пересечений по времени.

Связанные слои:
   - бизнес-логика — в `src/services/slot.py`.
"""

import uuid
from datetime import time
from typing import Any, Sequence

from sqlalchemy import Select, exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.crud.base import CRUDBase
from src.models import Slot
from src.schemas import TimeSlotCreate, TimeSlotUpdate


class CRUDSlot(CRUDBase):
    """CRUD класс для модели Slot."""

    def _stmt_with_cafe(self) -> Select[tuple[Slot]]:
        """Соберёт запрос с предзагрузкой кафе."""
        return select(self.model).options(selectinload(self.model.cafe))

    async def _reload_with_cafe(
        self,
        session: AsyncSession,
        slot_id: uuid.UUID,
    ) -> Slot:
        """Перечитает временной слот из БД с предзагруженным кафе."""
        result = await session.execute(
            self._stmt_with_cafe().where(self.model.id == slot_id),
        )
        return result.scalars().one()

    async def exists_overlapping(
        self,
        cafe_id: uuid.UUID,
        start_time: time,
        end_time: time,
        session: AsyncSession,
        exclude_id: uuid.UUID | None = None,
    ) -> bool | None:
        """Ищет временной слот этого кафе, пересекающийся по времени."""
        overlap_filters = [
            Slot.cafe_id == cafe_id,
            Slot.start_time < end_time,
            Slot.end_time > start_time,
        ]
        if exclude_id is not None:
            overlap_filters.append(Slot.id != exclude_id)

        query = select(exists().where(*overlap_filters))

        return await session.scalar(query)

    async def get(
        self,
        session: AsyncSession,
        *filters: Any,
    ) -> Slot | None:
        """Вернёт временной слот с предзагруженными кафе."""
        stmt = self._stmt_with_cafe()
        if filters:
            stmt = stmt.where(*filters)
            self._check_filters(*filters)
        result = await session.execute(stmt)
        return result.scalars().first()

    async def get_multi(
        self,
        session: AsyncSession,
        *filters: Any,
    ) -> Sequence[Slot]:
        """Вернёт список временных слотов с предзагруженными кафе."""
        stmt = self._stmt_with_cafe()
        if filters:
            stmt = stmt.where(*filters)
            self._check_filters(*filters)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def create(
        self,
        create_data: TimeSlotCreate,
        session: AsyncSession,
        **relations: Any,
    ) -> Slot:
        """Создаст временной слот и вернёт его с предзагруженными кафе."""
        slot = await super().create(create_data, session, **relations)
        return await self._reload_with_cafe(session, slot.id)

    async def update(
        self,
        db_entity: Slot,
        update_data: TimeSlotUpdate,
        session: AsyncSession,
        **relations: Any,
    ) -> Slot:
        """Обновит временной слот и вернёт его с предзагруженными кафе."""
        slot = await super().update(db_entity, update_data, session, **relations)
        return await self._reload_with_cafe(session, slot.id)


slot_crud = CRUDSlot(Slot)
