import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.models import Cafe


class CRUDCafe(CRUDBase):
    """CRUD функции для модели Cafe."""

    async def get_managers_by_cafe(
        self,
        cafe_id: uuid.UUID,
        session: AsyncSession,
    ) -> list[Optional[uuid.UUID]]:
        """Возвращает список id менеджеров связанных с определённого кафе."""
        result = await session.execute(select(self.model.managers.id).where(
            self.model.id == cafe_id,
        ))
        return list(result.scalars().all())

    async def get_cafes_by_manager(
        self,
        manager_id: uuid.UUID,
        session: AsyncSession,
    ) -> Optional[uuid.UUID]:
        """Возвращает id кафе связанное с определённым менеджером."""
        result = await session.execute(select(self.model.id).where(
            self.model.managers.id == manager_id,
        ))
        return result.scalars().first()


cafe_crud = CRUDCafe(Cafe)
