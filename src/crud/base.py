import uuid
from typing import Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession


class CRUDBase:
    """Базовый CRUD класс."""

    def __init__(self, model) -> None:  # noqa: ANN001, D107
        self.model = model

    async def get(  # noqa: ANN201
        self,
        session: AsyncSession,
        *filters,  # noqa: ANN002
    ):
        """GET-функция, возвращает объект по заданным фильтрам.

        Пример:
        ```
        await dish_crud.get(
            session,
            Dish.name == name,
        )
        ```
        """
        result = await session.execute(
            select(self.model).where(*filters),
        )
        return result.scalars().first()

    async def get_multi(  # noqa: ANN201
        self,
        session: AsyncSession,
        *filters,  # noqa: ANN002
    ):
        """GET-функция, возвращает список объектов."""
        stmt = select(self.model)

        if filters:
            stmt = stmt.where(*filters)

        result = await session.execute(stmt)

        return result.scalars().all()

    async def create(  # noqa: ANN201
        self,
        obj_in,  # noqa: ANN001
        session: AsyncSession,
    ):
        """POST-функция, добавляет объект в базу данных."""
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(  # noqa: ANN201
        self,
        db_obj,  # noqa: ANN001
        obj_in,  # noqa: ANN001
        session: AsyncSession,
    ):
        """PATCH-функция, обновляет информацю об объекте в базе данных."""
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.model_dump(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def exists(
        self,
        session: AsyncSession,
        *filters,  # noqa: ANN002
    ) -> Optional[bool]:
        """Запрос для проверки существования объекта."""
        result = select(
            exists().where(*filters),
        )

        return await session.scalar(result)
