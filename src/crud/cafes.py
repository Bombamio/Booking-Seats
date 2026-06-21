from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase
from models import Cafes


class CRUDCafes(CRUDBase):

    async def get_managers_by_cafe(
        self,
        cafe_id: int,
        session: AsyncSession
    ) -> list[Optional[int]]:
        """
        Возвращает список id менеджеров связанных с определённого кафе.
        """

        result = await session.execute(select(self.model.managers.id).where(
            self.model.id == cafe_id,
        ))
        return list(result.scalars().all())

    async def get_cafes_by_manager(
        self,
        manager_id: int,
        session: AsyncSession
    ) -> Optional[int]:
        """
        Возвращает id кафе связанное с определённым менеджером.
        """

        result = await session.execute(select(self.model.id).where(
            self.model.managers.id == manager_id,
        ))
        return result.scalars().first()


cafes_crud = CRUDCafes(Cafes)
