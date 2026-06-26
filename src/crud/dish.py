import uuid

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.models import Dish, User
from src.core.cache import cache
from src.core.settings import settings


class CRUDDish(CRUDBase):
    """CRUD функции для модели Dish."""

    async def duplicate_exists(
        self,
        user: User,
        cafe_id: Optional[uuid.UUID],
        session: AsyncSession,
        show_active: bool = True,
    ):
        """Получение списка блюд. Для администраторов и менеджеров - все
        блюда (с возможностью выбора), для пользователей - только активные.
        """  # noqa: D205
        cache_key = (
            f"dishes:cafe:{cafe_id}:user:{user.id}:"
            f"active:{show_active}"
        )
        cached_data = await cache.get(cache_key)
        if cached_data is not None:
            return cached_data

        filters = []

        if cafe_id is not None:
            filters.append(self.model.cafe_id == cafe_id)

        # Супер пользователь видит либо все, либо только неактивне блюда.
        if user.role.ADMIN:
            if show_active is False:
                filters.append(self.model.is_active.is_(False))
        elif user.role.MANAGER:
            # TODO: Я совсем не уверен в этом поле, но выглядит убедительно.
            filters.append(self.model.cafes.managers.id == user.id)
            filters.append(self.model.is_active.is_(show_active))

        else:
            filters.append(self.model.is_active.is_(True))

        result = await session.execute(select(self.model).where(*filters))
        data = list(result.scalars().all())

        await cache.set(cache_key, data, settings.cache_expire_menu)

        return data


dish_crud = CRUDDish(Dish)
