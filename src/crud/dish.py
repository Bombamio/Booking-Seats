import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.models import Dish, User


class CRUDDish(CRUDBase):
    """CRUD функции для модели Dish."""

    async def get_list_by_user(  # noqa: ANN201
        self,
        user: User,
        cafe_id: Optional[uuid.UUID],
        session: AsyncSession,
        show_active: bool = True,
    ):
        """Получение списка блюд. Для администраторов и менеджеров - все
        блюда (с возможностью выбора), для пользователей - только активные.
        """  # noqa: D205
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
        return list(result.scalars().all())

    async def get_by_name(  # noqa: ANN201
        self,
        cafe_id: uuid.UUID,
        name: str,
        session: AsyncSession,
    ):
        """Ищет блюдо по имени в определённом кафе."""
        result = await session.execute(
            select(self.model).where(
                self.model.cafe_id == cafe_id,
                self.model.name == name,
            ),
        )
        return result.scalars().first()

    async def get_by_user(  # noqa: ANN201
        self,
        user: User,
        dish: Dish,
        session: AsyncSession,
    ):
        """Получение информации о блюде по его ID. Для администраторов и
        менеджеров - все блюда, для пользователей - только активные.
        """  # noqa: D205
        filters = []
        if not user.role.ADMIN and not user.role.MANAGER:
            filters.append(self.model.is_active.is_(True))
        elif user.role.MANAGER:
            # TODO: Я совсем не уверен в этом поле, но выглядит убедительно.
            filters.append(self.model.cafes.managers.id == user.id)
        filters.append(self.model.id == dish.id)

        result = await session.execute(select(self.model).where(*filters))
        return result.scalars().first()


dish_crud = CRUDDish(Dish)
