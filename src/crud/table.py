from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.models import Table


class CRUDTable(CRUDBase):
    """Класс для обработки обращений к данным модели Table в БД."""

    async def get_by_cafe(
        self,
        cafe_id: UUID,
        session: AsyncSession,
    ) -> list[Table]:
        """Вернет все столы заданного кафе."""
        tables = await session.execute(
            select(self.model).where(self.model.cafe_id == cafe_id),
        )
        return tables.scalars().all()


table_crud = CRUDTable(Table)
