import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.models import Slot
from src.schemas import TimeSlotCreate


class CRUDSlot(CRUDBase):
    """CRUD класс для модели Slot."""

    async def get_multi_by_cafe(
        self,
        cafe_id: uuid.UUID,
        session: AsyncSession,
        show_active: bool = True,
    ) -> list[Slot]:
        """Возвращает список временных слотов конкретного кафе."""
        query = select(self.model).where(self.model.cafe_id == cafe_id)
        if show_active:
            query = query.where(self.model.is_active.is_(True))

        result = await session.execute(query)
        return result.scalars().all()

    async def get_overlapping(
        self,
        cafe_id: uuid.UUID,
        start_time: datetime,
        end_time: datetime,
        session: AsyncSession,
        exclude_id: Optional[uuid.UUID] = None,
    ) -> Optional[Slot]:
        """Ищет временной слот этого кафе, пересекающийся по времени."""
        query = select(self.model).where(
            self.model.cafe_id == cafe_id,
            self.model.start_time < end_time,
            self.model.end_time > start_time,
        )
        if exclude_id is not None:
            query = query.where(self.model.id != exclude_id)

        result = await session.execute(query)
        return result.scalars().first()

    async def create_with_cafe(
        self,
        slot_create: TimeSlotCreate,
        cafe_id: uuid.UUID,
        session: AsyncSession,
    ) -> Slot:
        """Создаёт временной слот, привязанный к переданному кафе."""
        slot_data = {
            key: value
            for key, value in slot_create.model_dump().items()
            if key in self.model_fields
        }
        slot_entity = self.model(
            cafe_id=cafe_id,
            **slot_data,
        )
        session.add(slot_entity)
        await session.flush()
        await session.refresh(slot_entity)
        return slot_entity


slot_crud = CRUDSlot(Slot)
