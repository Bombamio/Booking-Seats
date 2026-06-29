import uuid
from typing import Any, Optional

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.inspection import inspect
from sqlalchemy.sql.elements import BinaryExpression

from src.core.logger import bookingseats_logger


class CRUDBase:
    """Базовый CRUD класс."""

    def __init__(
        self,
        model: Any,
    ) -> None:
        """Метаданные модели."""
        self.model = model
        self.mapper = inspect(self.model)
        self.model_fields = set(self.mapper.columns.keys())
        self.relationships = set(self.mapper.relationships.keys())

    @staticmethod
    def _format_filters(*filters: Any) -> str:
        """Сформирует строку с описанием применённых фильтров."""
        if not filters:
            return 'нет'
        return ', '.join(str(filter_) for filter_ in filters)

    def _check_filters(
        self,
        *filters: Any,
    ) -> None:
        """Проверка простых бинарных выражений."""
        table = self.model.__table__

        for filter_ in filters:
            if isinstance(filter_, BinaryExpression):
                if filter_.left.table is not table:
                    raise ValueError(
                        f'Invalid filter: {filter_}',
                    )

    async def get(
        self,
        session: AsyncSession,
        *filters: Any,
    ) -> Any:
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

        self._check_filters(*filters)
        result = await session.execute(
            select(self.model).where(*filters),
        )
        return result.scalars().first()

    async def get_multi(
        self,
        session: AsyncSession,
        *filters: Any,
    ) -> Any:
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
            self._check_filters(*filters)

        bookingseats_logger.debug(
            f'get_multi {self.model.__name__}: '
            f'filters=[{self._format_filters(*filters)}]',
        )
        result = await session.execute(stmt)

        return result.scalars().all()

    async def create(
        self,
        obj_in: Any,
        session: AsyncSession,
        **relations: Any,
    ) -> Any:
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
        obj_in_data = {
            key: value
            for key, value in obj_in.model_dump().items()
            if key in self.model_fields
        }
        db_obj = self.model(**obj_in_data)

        for attr, value in relations.items():
            if attr not in self.relationships:
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

    async def update(
        self,
        db_obj: Any,
        obj_in: Any,
        session: AsyncSession,
        **relations: Any,
    ) -> Any:
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

        for field, value in update_data.items():
            if field in self.model_fields:
                setattr(db_obj, field, value)

        for attr, value in relations.items():
            if attr not in self.relationships:
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
        *filters: Any,
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

        self._check_filters(*filters)
        result = select(
            exists().where(*filters),
        )

        return await session.scalar(result)

    async def duplicate_exists(
        self,
        name: str,
        exclude_id: Optional[uuid.UUID],
        session: AsyncSession,
    ) -> Optional[bool]:
        """Проверяет, существует ли объект с таким именем."""
        filters = [self.model.name == name]
        if exclude_id is not None:
            # Текущее объект не считается дубликатом.
            filters.append(self.model.id != exclude_id)
        result = select(
            exists().where(
                *filters,
            ),
        )

        return await session.scalar(result)
