import uuid
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.cache import cache
from src.core.settings import settings
from src.crud.base import CRUDBase
from src.crud.cafe import cafe_crud
from src.models import Action, Cafe
from src.schemas import ActionCreate, ActionUpdate


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
        action_create: ActionCreate,
        session: AsyncSession,
    ) -> Action:
        """Создание акции с привязкой к кафе."""
        if not action_create.cafes_id:
            raise ValueError(
                'Акция должна быть привязана хотя бы к одному кафе',
            )

        cafes = await cafe_crud.get_multi(
            session,
            Cafe.id.in_(action_create.cafes_id),
        )

        return await super().create(
            create_data=action_create,
            session=session,
            cafes=cafes,
        )

    async def update(
        self,
        action_entity: Action,
        action_update: ActionUpdate,
        session: AsyncSession,
    ) -> Action:
        """Обновление акции, включая связи с кафе."""
        relations = {}

        if action_update.cafes_id is not None:
            if not action_update.cafes_id:
                raise ValueError(
                    'Акция должна быть привязана хотя бы к одному кафе',
                )

            cafes = await cafe_crud.get_multi(
                session,
                Cafe.id.in_(action_update.cafes_id),
            )
            relations['cafes'] = cafes

        return await super().update(
            db_entity=action_entity,
            update_data=action_update,
            session=session,
            **relations,
        )

    async def get_active_actions(
        self,
        cafe_id: Optional[uuid.UUID],
        session: AsyncSession,
    ) -> List[Action]:
        """Получение активных акций с кешированием."""
        cache_key = f'actions:cafe:{cafe_id}:active'

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
            await cache.delete(f'actions:cafe:{cafe_id}:active')
        await cache.clear_pattern('actions:cafe:*')


action_crud = CRUDAction(Action)
