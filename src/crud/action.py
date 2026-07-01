import uuid
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.cache import cache
from src.core.settings import settings
from src.crud.base import CRUDBase
from src.models import Action
from src.models.cafe import Cafe
from src.schemas.action import ActionCreate, ActionUpdate


class CRUDAction(CRUDBase):
    """CRUD функции для модели Action."""

    async def get_multi(
        self,
        session: AsyncSession,
        active: Optional[bool] = None,
        cafe_id: Optional[uuid.UUID] = None,
    ) -> List[Action]:
        """Получение списка акций с фильтрацией."""
        filters = []

        if active is not None:
            filters.append(self.model.is_active == active)

        if cafe_id:
            filters.append(self.model.cafes.any(Cafe.id == cafe_id))

        return await super().get_multi(session, *filters)

    async def create(
        self,
        obj_in: ActionCreate,
        session: AsyncSession,
    ) -> Action:
        """Создание акции с привязкой к кафе."""
        if not obj_in.cafes_id:
            raise ValueError(
                'Акция должна быть привязана хотя бы к одному кафе',
            )

        cafes = await Cafe.get_multi(
            session,
            Cafe.id.in_(obj_in.cafes_id),
        )

        return await super().create(
            obj_in=obj_in,
            session=session,
            cafes=cafes,
        )

    async def update(
        self,
        db_obj: Action,
        obj_in: ActionUpdate,
        session: AsyncSession,
    ) -> Action:
        """Обновление акции, включая связи с кафе."""
        relations = {}

        if obj_in.cafes_id is not None:
            if not obj_in.cafes_id:
                raise ValueError(
                    'Акция должна быть привязана хотя бы к одному кафе',
                )

            cafes = await Cafe.get_multi(
                session,
                Cafe.id.in_(obj_in.cafes_id),
            )
            relations['cafes'] = cafes

        return await super().update(
            db_obj=db_obj,
            obj_in=obj_in,
            session=session,
            **relations,
        )

    async def get_active_actions(
        self,
        cafe_id: Optional[uuid.UUID],
        session: AsyncSession,
    ):
        """Получение активных акций с кешированием."""
        cache_key = f"actions:cafe:{cafe_id}:active"

        cached_data = await cache.get(cache_key)
        if cached_data:
            return cached_data

        data = await self.get_multi(
            session=session,
            active=True,
            cafe_id=cafe_id,
        )
        await cache.set(cache_key, data, settings.CACHE_EXPIRE_ACTIONS)

        return data

    async def clear_cache(
        self,
        cafe_id: Optional[uuid.UUID],
    ) -> None:
        """Очистка кеша акций."""
        if cafe_id:
            await cache.delete(f"actions:cafe:{cafe_id}:active")
        await cache.clear_pattern("actions:cafe:*")


action_crud = CRUDAction(Action)
