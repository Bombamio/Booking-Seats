import uuid
from datetime import time
from typing import Any, Optional, Sequence

from sqlalchemy import Select, exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.crud.base import CRUDBase
from src.models import Cafe, Slot
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
        exclude_id: Optional[uuid.UUID] = None,
    ) -> Optional[bool]:
        """Ищет временной слот этого кафе, пересекающийся по времени."""
        query = select(
            exists().where(
                Slot.cafe.any(Cafe.id == cafe_id),
                Slot.start_time < end_time,
                Slot.end_time > start_time,
            ),
        )
        if exclude_id is not None:
            query = query.where(self.model.id != exclude_id)

        return await session.scalar(query)

    async def get(
        self,
        session: AsyncSession,
        *filters: Any,
    ) -> Optional[Slot]:
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
