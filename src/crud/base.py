from typing import Optional

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.inspection import inspect

from src.core.logger import bookingseats_logger


class CRUDBase:
    """Базовый CRUD класс."""

    def __init__(self, model) -> None:  # noqa: ANN001, D107
        self.model = model

    @staticmethod
    def _format_filters(*filters) -> str:  # noqa: ANN002
        """Сформирует строку с описанием применённых фильтров."""
        if not filters:
            return 'нет'
        return ', '.join(str(filter_) for filter_ in filters)

    async def get(  # noqa: ANN201
        self,
        session: AsyncSession,
        *filters,  # noqa: ANN002
    ):
        """GET-функция, возвращает объект по заданным фильтрам.

        Пример:
        ```
        dish: Dish = await dish_crud.get(
            session,
            Dish.name == name,
            Dish.is_active.is_(True),
        )
        ```
        """
        bookingseats_logger.debug(
            f'get {self.model.__name__}: '
            f'filters=[{self._format_filters(*filters)}]',
        )
        result = await session.execute(
            select(self.model).where(*filters),
        )
        return result.scalars().first()

    async def get_multi(  # noqa: ANN201
        self,
        session: AsyncSession,
        *filters,  # noqa: ANN002
    ):
        """GET-функция, возвращает список объектов.

        Пример:
        ```
        dishes: list[Dish] = await dish_crud.get_multi(
            session,
            Dish.cafes.any(Cafe.id == cafe_id),
            Dish.is_active.is_(True),
        )
        ```
        """
        stmt = select(self.model)

        if filters:
            stmt = stmt.where(*filters)

        bookingseats_logger.debug(
            f'get_multi {self.model.__name__}: '
            f'filters=[{self._format_filters(*filters)}]',
        )
        result = await session.execute(stmt)

        return result.scalars().all()

    async def create(  # noqa: ANN201
        self,
        obj_in,  # noqa: ANN001
        session: AsyncSession,
        **relations,  # noqa: ANN003
    ):
        """POST-функция, добавляет объект в базу данных.

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
        bookingseats_logger.debug(
            f'create {self.model.__name__} id={db_obj.id}: '
            f'data={obj_in_data}, relations={list(relations.keys())}',
        )
        await session.commit()
        await session.refresh(db_obj)

        return db_obj

    async def update(  # noqa: ANN201
        self,
        db_obj,  # noqa: ANN001
        obj_in,  # noqa: ANN001
        session: AsyncSession,
        **relations,  # noqa: ANN003
    ):
        """PATCH-функция, обновляет информацю об объекте в базе данных.

        **Примечание!** Если у вас есть поле many-to-many - обязательно
        впишите его в функцию.

        Пример:
        ```
        relations = {}

        if obj_in.cafes_id is not None:
            cafes = await cafe_crud.get_multi(
                session,
                Cafe.id.in_(obj_in.cafes_id),
            )
            relations['cafes'] = cafes

        return await dish_crud.update(
            db_obj=dish,
            obj_in=obj_in,
            session=session,
            **relations,
        )
        ```
        """
        update_data = obj_in.model_dump(exclude_unset=True)

        model_fields = self.model.__table__.columns.keys()

        for field, value in update_data.items():
            if field in model_fields:
                setattr(db_obj, field, value)

        mapper = inspect(self.model)

        for attr, value in relations.items():
            if attr not in mapper.relationships:
                # Защита от опечаток.
                raise ValueError(
                    f'{attr} is not a relationships of {self.model.__name__}',
                )
            setattr(db_obj, attr, value)

        session.add(db_obj)
        bookingseats_logger.debug(
            f'update {self.model.__name__} id={db_obj.id}: '
            f'data={update_data}, relations={list(relations.keys())}',
        )
        await session.commit()
        await session.refresh(db_obj)

        return db_obj

    async def exists(
        self,
        session: AsyncSession,
        *filters,  # noqa: ANN002
    ) -> Optional[bool]:
        """Запрос для проверки существования объекта.

        Пример:
        ```
        await dish_crud.exists(
            session,
            Dish.name == name,
            Dish.is_active.is_(True),
        )
        ```
        """
        bookingseats_logger.debug(
            f'exists {self.model.__name__}: '
            f'filters=[{self._format_filters(*filters)}]',
        )
        result = select(
            exists().where(*filters),
        )

        return await session.scalar(result)
