import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.crud.base import CRUDBase
from src.models import Action
from src.core.cache import cache
from src.core.settings import settings


class CRUDAction(CRUDBase):
    """CRUD функции для модели Action."""

    async def get_active_actions(
        self,
        cafe_id: Optional[uuid.UUID] = None,
        session: AsyncSession = None,
    ):
        """Получение активных акций с кешированием."""
        cache_key = f"actions:cafe:{cafe_id}:active"

        cached_data = await cache.get(cache_key)
        if cached_data:
            return cached_data

        filters = [self.model.is_active.is_(True)]
        if cafe_id:
            filters.append(self.model.cafes.any(id=cafe_id))

        result = await session.execute(select(self.model).where(*filters))
        data = list(result.scalars().all())
        await cache.set(cache_key, data, settings.CACHE_EXPIRE_ACTIONS)

        return data

    async def clear_cache(self, cafe_id: Optional[uuid.UUID] = None):
        """Очистка кеша акций."""
        if cafe_id:
            await cache.delete(f"actions:cafe:{cafe_id}:active")
        await cache.clear_pattern("actions:cafe:*")
