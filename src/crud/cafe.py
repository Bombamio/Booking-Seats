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
        cafe_create,  # noqa: ANN001
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
            create_data=dish_data,
            session=session,
            cafes=cafes,
        )
        ```
        """
        model_fields = self.model.__table__.columns.keys()

        cafe_payload = {key: value for key, value in cafe_create.model_dump().items() if key in model_fields}

        cafe_entity = self.model(**cafe_payload)

        mapper = inspect(self.model)

        for attr, value in relations.items():
            if attr not in mapper.relationships:
                # Защита от опечаток.
                raise ValueError(
                    f'{attr} is not a relationships of {self.model.__name__}',
                )
            setattr(cafe_entity, attr, value)

        session.add(cafe_entity)
        await session.flush()

        return cafe_entity

    async def get_multi_with_managers(
        self,
        session: AsyncSession,
        *filters,  # noqa: ANN002
    ) -> list[Cafe]:
        """GET-функция, возвращает список объектов.

        С подгрузкой менеджеров через relationships.
        """
        stmt = select(self.model).options(selectinload(Cafe.managers)).where(*filters)
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
            select(self.model).options(selectinload(Cafe.managers)).where(*filters),
        )
        return result.scalars().first()

    async def update_cafe(
        self,
        cafe_entity,  # noqa: ANN001
        cafe_update,  # noqa: ANN001
        session: AsyncSession,
    ) -> Cafe:
        """PATCH-функция, обновляет информацю о кафе.

        Commit должен выполняться на стороне сервиса
        """
        cafe_update_payload = cafe_update.model_dump(exclude_unset=True)

        model_fields = self.model.__table__.columns.keys()

        for field, value in cafe_update_payload.items():
            if field in model_fields:
                setattr(cafe_entity, field, value)

        session.add(cafe_entity)
        await session.flush()

        return cafe_entity


cafe_crud = CRUDCafe(Cafe)
