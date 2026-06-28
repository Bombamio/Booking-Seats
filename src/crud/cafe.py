from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import selectinload

from src.crud.base import CRUDBase
from src.models import Cafe


class CRUDCafe(CRUDBase):
    """CRUD функции для модели Cafe."""

    async def create_cafe(  # noqa: ANN201
        self,
        obj_in,  # noqa: ANN001
        session: AsyncSession,
        **relations,  # noqa: ANN003
    ):
        """Метод создает объект, но не делает commit.

        Commit должен выполняться на стороне сервиса

        **Примечание!** Если у вас есть поле many-to-many - обязательно
        впишите его в функцию.

        Пример:
        ```
        return await dish_crud.create(
            obj_in=obj_in,
            session=session,
            cafes=cafes,
        )
        ```
        """
        model_fields = self.model.__table__.columns.keys()

        obj_in_data = {
            key: value
            for key, value in obj_in.model_dump().items()
            if key in model_fields
        }

        db_obj = self.model(**obj_in_data)

        mapper = inspect(self.model)

        for attr, value in relations.items():
            if attr not in mapper.relationships:
                # Защита от опечаток.
                raise ValueError(
                    f'{attr} is not a relationships of {self.model.__name__}',
                )
            setattr(db_obj, attr, value)

        session.add(db_obj)
        await session.flush()

        return db_obj

    async def get_multi_with_managers(
        self,
        session: AsyncSession,
        *filters,  # noqa: ANN002
    ) -> list[Cafe]:
        """GET-функция, возвращает список объектов.

        С подгрузкой менеджеров через relationships.
        """
        stmt = (
            select(self.model)
            .options(selectinload(Cafe.managers))
            .where(*filters)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_with_managers(
        self,
        session: AsyncSession,
        *filters,  # noqa: ANN002
    ) -> Cafe:
        """GET-функция, возвращает объект по заданным фильтрам.

        С подгрузкой менеджеров через relationships.
        """
        result = await session.execute(
            select(self.model)
            .options(selectinload(Cafe.managers))
            .where(*filters),
        )
        return result.scalars().first()

    async def update_cafe(
        self,
        db_obj,  # noqa: ANN001
        obj_in,  # noqa: ANN001
        session: AsyncSession,
    ) -> Cafe:
        """PATCH-функция, обновляет информацю о кафе.

        Commit должен выполняться на стороне сервиса
        """
        update_data = obj_in.model_dump(exclude_unset=True)

        model_fields = self.model.__table__.columns.keys()

        for field, value in update_data.items():
            if field in model_fields:
                setattr(db_obj, field, value)

        session.add(db_obj)
        await session.flush()

        return db_obj


cafe_crud = CRUDCafe(Cafe)
