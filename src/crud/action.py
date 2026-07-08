import uuid
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import Select

from src.core.cache import cache
from src.core.settings import settings
from src.crud.base import CRUDBase
from src.crud.cafe import cafe_crud
from src.models import Action, Cafe
from src.schemas import ActionCreate, ActionUpdate


class CRUDAction(CRUDBase):
    """CRUD функции для модели Action."""

    def _stmt_with_cafes(self) -> Select[tuple[Action]]:
        """Соберёт запрос с предзагрузкой связанных кафе."""
        return select(self.model).options(selectinload(self.model.cafes))

    async def get(
        self,
        session: AsyncSession,
        *filters: Any,
    ) -> Action | None:
        """Вернёт акцию с предзагруженными кафе."""
        stmt = self._stmt_with_cafes()
        if filters:
            stmt = stmt.where(*filters)
            self._check_filters(*filters)
        result = await session.execute(stmt)
        return result.scalars().first()

    async def get_multi(
        self,
        session: AsyncSession,
        active: Optional[bool] = None,
        cafe_id: Optional[uuid.UUID] = None,
    ) -> list[Action]:
        """Получение списка акций с фильтрацией."""
        filters = []

        if active is not None:
            filters.append(self.model.is_active == active)

        if cafe_id:
            filters.append(self.model.cafes.any(Cafe.id == cafe_id))

        stmt = self._stmt_with_cafes()
        if filters:
            stmt = stmt.where(*filters)
            self._check_filters(*filters)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def _reload_with_cafes(
        self,
        session: AsyncSession,
        action_id: uuid.UUID,
    ) -> Action:
        """Перечитает акцию из БД с предзагруженными кафе."""
        result = await session.execute(
            self._stmt_with_cafes().where(self.model.id == action_id),
        )
        return result.scalars().one()

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

        action = await super().create(
            create_data=action_create,
            session=session,
            cafes=cafes,
        )
        return await self._reload_with_cafes(session, action.id)

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

        action = await super().update(
            db_entity=action_entity,
            update_data=action_update,
            session=session,
            **relations,
        )
        return await self._reload_with_cafes(session, action.id)

    async def get_active_actions(
        self,
        cafe_id: Optional[uuid.UUID],
        session: AsyncSession,
    ) -> list[Action]:
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
