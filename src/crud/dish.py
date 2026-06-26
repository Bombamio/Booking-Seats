import uuid

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.models import Dish


class CRUDDish(CRUDBase):
    """CRUD функции для модели Dish."""

    async def duplicate_exists(
        self,
        name: str,
        session: AsyncSession,
        exclude_id: uuid.UUID | None = None,
    ) -> bool:
        """Проверяет, существует ли блюдо с таким именем."""
        filters = [self.model.name == name]
        if exclude_id is not None:
            # Текущее блюдо не считается дубликатом.
            filters.append(self.model.id != exclude_id)
        result = select(
            exists().where(
                *filters,
            ),
        )
        return await session.scalar(result)


dish_crud = CRUDDish(Dish)
