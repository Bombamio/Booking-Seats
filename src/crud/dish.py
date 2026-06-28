import uuid
from typing import Optional

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.cache import cache
from src.core.settings import settings
from src.crud.base import CRUDBase
from src.models import Dish


class CRUDDish(CRUDBase):
    """CRUD функции для модели Dish."""

    async def duplicate_exists(
        self,
        name: str,
        session: AsyncSession,
        exclude_id: Optional[uuid.UUID],
    ):
        """Проверяет, существует ли блюдо с таким именем."""
        # TODO: Нужно переработать cache.
        cache_key = (
            f"dishes:cafe:{cafe_id}:user:{user.id}:"
            f"active:{show_active}"
        )
        cached_data = await cache.get(cache_key)
        if cached_data is not None:
            return cached_data

        filters = [self.model.name == name]
        if exclude_id is not None:
            # Текущее блюдо не считается дубликатом.
            filters.append(self.model.id != exclude_id)
        result = select(
            exists().where(
                *filters,
            ),
        )

        result = await session.scalar(result)
        data = list(result.scalars().all())

        await cache.set(cache_key, data, settings.cache_expire_menu)

        return data


dish_crud = CRUDDish(Dish)
