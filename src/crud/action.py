import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.cache import cache
from src.core.settings import settings
from src.crud.base import CRUDBase
from src.models import Action
from src.models.cafe import Cafe
from src.schemas.action import ActionCreate, ActionUpdate


class CRUDAction(CRUDBase):
    """CRUD функции для модели Action."""

    async def get(
        self,
        obj_id,
        session: AsyncSession,
    ) -> Optional[Action]:
        """Получение акции с загрузкой связанных кафе."""
        result = await session.execute(
            select(self.model)
            .options(selectinload(self.model.cafes))
            .where(self.model.id == obj_id),
        )
        return result.unique().scalars().first()

    async def get_multi(
        self,
        session: AsyncSession,
        active: Optional[bool] = None,
        cafe_id=None,
    ) -> List[Action]:
        """Получение списка акций с фильтрацией."""
        query = (
            select(self.model)
            .options(selectinload(self.model.cafes))
        )

        if active is not None:
            query = query.where(self.model.is_active == active)

        if cafe_id:
            query = query.where(
                self.model.cafes.any(Cafe.id == cafe_id)
            )

        result = await session.execute(query)
        return list(result.unique().scalars().all())

    async def create(
        self,
        obj_in: ActionCreate,
        session: AsyncSession,
    ) -> Action:
        """Создание акции с привязкой к кафе."""
        cafes_ids = obj_in.cafes_id or []
        action_data = obj_in.model_dump(exclude={'cafes_id'})

        cafes = []
        if cafes_ids:
            cafes_result = await session.execute(
                select(Cafe).where(Cafe.id.in_(cafes_ids))
            )
            cafes = cafes_result.scalars().all()

        db_obj = self.model(**action_data)
        db_obj.cafes = cafes

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db_obj: Action,
        obj_in: ActionUpdate,
        session: AsyncSession,
    ) -> Action:
        """Обновление акции, включая связи с кафе."""
        update_data = obj_in.model_dump(exclude_unset=True)

        cafes_ids = update_data.pop('cafes_id', None)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        if cafes_ids is not None:
            if cafes_ids:
                cafes_result = await session.execute(
                    select(Cafe).where(Cafe.id.in_(cafes_ids))
                )
                db_obj.cafes = cafes_result.scalars().all()
            else:
                db_obj.cafes = []

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

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

        filters = [self.model.is_active.is_(True)]
        if cafe_id:
            filters.append(self.model.cafes.any(id=cafe_id))

        result = await session.execute(select(self.model).where(*filters))
        data = list(result.scalars().all())
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
