from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase
from models import Dishes


class CRUDDishes(CRUDBase):

    async def get_by_user(
        self,
        user: User,
        cafe_id: Optional[int],
        session: AsyncSession,
        show_active: bool = True,
    ):
        """
        Получение списка блюд. Для администраторов и менеджеров - все
        блюда (с возможностью выбора), для пользователей - только активные.
        """

        # Создаётся список фильтров чтобы не повтарятся в запросах.
        filters = []

        if cafe_id is not None:
            filters.append(self.model.cafe_id == cafe_id)

        # Супер пользователь видит либо все, либо только неактивне блюда.
        if user.superuser:
            if show_active is False:
                filters.append(self.model.is_active.is_(False))
        elif user.manager:
            filters.append(self.model.is_active.is_(show_active))

        else:
            filters.append(self.model.is_active.is_(True))

        result = await session.execute(select(self.model).where(*filters))
        return list(result.scalars().all())


dishes_crud = CRUDDishes(Dishes)
