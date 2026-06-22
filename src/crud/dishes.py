from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.base import CRUDBase
from models import Dishes, User


class CRUDDishes(CRUDBase):

    async def get_list_by_user(
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
        if user.role.superuser:
            if show_active is False:
                filters.append(self.model.is_active.is_(False))
        elif user.role.manager:
            # TODO: Я совсем не уверен в этом поле, но выглядит убедительно.
            filters.append(self.model.cafes.managers.id == user.id)
            filters.append(self.model.is_active.is_(show_active))

        else:
            filters.append(self.model.is_active.is_(True))

        result = await session.execute(select(self.model).where(*filters))
        return list(result.scalars().all())

    async def get_by_name(
        self,
        cafe_id: int,
        name: str,
        session: AsyncSession
    ):
        """
        Ищет блюдо по имени в определённом кафе.
        """

        result = await session.execute(select(self.model).where(
            self.model.cafe_id == cafe_id,
            self.model.name == name,
        ))
        return result.scalars().first()

    async def get_by_user(
        self,
        user: User,
        dish: Dishes,
        session: AsyncSession,
    ):
        """
        Получение информации о блюде по его ID. Для администраторов и
        менеджеров - все блюда, для пользователей - только активные.
        """

        filters = []
        if not user.role.superuser and not user.role.manager:
            filters.append(self.model.is_active.is_(True))
        elif user.role.manager:
            # TODO: Я совсем не уверен в этом поле, но выглядит убедительно.
            filters.append(self.model.cafes.managers.id == user.id)
        filters.append(self.model.id == dish.id)

        result = await session.execute(select(self.model).where(*filters))
        return result.scalars().first()


dishes_crud = CRUDDishes(Dishes)
