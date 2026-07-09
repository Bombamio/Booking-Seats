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

    def _set_relation(self, entity: Any, relations: dict[str, Any]) -> None:
        for attr, value in relations.items():
            if attr not in self.relationships:
                # Защита от опечаток.
                raise ValueError(
                    f'{attr} is not a relationships of {self.model.__name__}',
                )
            setattr(entity, attr, value)

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
            f'get {self.model.__name__}: filters=[{self._format_filters(*filters)}]',
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
            f'get_multi {self.model.__name__}: filters=[{self._format_filters(*filters)}]',
        )
        result = await session.execute(stmt)

        return result.scalars().all()

    async def create(
        self,
        create_data: Any,
        session: AsyncSession,
        **relations: Any,
    ) -> Any:
        """POST-функция, добавляет объект в базу данных.

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
        create_payload = {
            key: value for key, value in create_data.model_dump().items() if key in self.model_fields
        }
        created_entity = self.model(**create_payload)

        self._set_relation(created_entity, relations)

        session.add(created_entity)
        await session.commit()
        bookingseats_logger.debug(
            f'create {self.model.__name__} id={created_entity.id}: '
            f'data={create_payload}, relations={list(relations.keys())}',
        )
        await session.refresh(created_entity)

        return created_entity

    async def update(
        self,
        db_entity: Any,
        update_data: Any,
        session: AsyncSession,
        **relations: Any,
    ) -> Any:
        """PATCH-функция, обновляет информацю об объекте в базе данных.

        **Примечание!** Если у вас есть поле many-to-many - обязательно
        впишите его в функцию.

        Пример:
        ```
        relations = {}

        if update_data.cafes_id is not None:
            cafes = await cafe_crud.get_multi(
                session,
                Cafe.id.in_(update_data.cafes_id),
            )
            relations['cafes'] = cafes

        return await dish_crud.update(
            db_entity=dish,
            update_data=update_data,
            session=session,
            **relations,
        )
        ```
        """
        update_payload = update_data.model_dump(exclude_unset=True)

        for field, value in update_payload.items():
            if field in self.model_fields:
                setattr(db_entity, field, value)

        self._set_relation(db_entity, relations)

        session.add(db_entity)
        bookingseats_logger.debug(
            f'update {self.model.__name__} id={db_entity.id}: '
            f'data={update_payload}, relations={list(relations.keys())}',
        )
        await session.commit()
        await session.refresh(db_entity)

        return db_entity

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
            f'exists {self.model.__name__}: filters=[{self._format_filters(*filters)}]',
        )

        self._check_filters(*filters)
        result = select(
            exists().where(*filters),
        )

        return await session.scalar(result)
