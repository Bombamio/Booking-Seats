"""Базовый миксин сервисного слоя."""

import uuid
from typing import Any, NoReturn

from fastapi import status
from sqlalchemy import inspect as sa_inspect
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import RelationshipDirection, load_only
from sqlalchemy.sql import select

from src.core.exceptions import BookingSeatsAppError
from src.core.logger import bookingseats_logger
from src.crud.base import CRUDBase
from src.models import User, UserRole


def is_active_filters(
    user: User,
    show_active: bool | None,
    is_active_column: Any,
) -> list[Any]:
    """Соберёт фильтры ``is_active`` по роли и параметру ``show_active``.

    * USER — всегда только активные (``show_active`` игнорируется).
    * ADMIN — без параметра все записи; ``true`` только активные;
      ``false`` только неактивные.
    * MANAGER — без параметра и ``true`` только активные;
      ``false`` только неактивные.
    """
    if user.role == UserRole.USER:
        return [is_active_column.is_(True)]

    if user.role == UserRole.ADMIN:
        if show_active is True:
            return [is_active_column.is_(True)]
        if show_active is False:
            return [is_active_column.is_(False)]
        return []

    if show_active is False:
        return [is_active_column.is_(False)]
    return [is_active_column.is_(True)]


class BaseService:
    """Базовый миксин сервисного слоя.

    Предложение одного из возможных вариантов реализации.
    Должен быть скорректирован позднее.
    Приведены методы, использование которых предполагается на примере сервиса
    для Table
    методы логирования и ошибки доступа реализованы как общие для почти всех сервисов

    """

    def log_info(
        self,
        message: str,
    ) -> None:
        """Запишет информационное сообщение в лог."""
        bookingseats_logger.info(message)

    def log_warning(
        self,
        message: str,
    ) -> None:
        """Запишет предупреждение в лог."""
        bookingseats_logger.warning(message)

    def raise_forbidden(
        self,
        message: str = 'Доступ запрещен',
    ) -> NoReturn:
        """Сообщит об ошибке доступа с кодом 403."""
        raise BookingSeatsAppError(
            status.HTTP_403_FORBIDDEN,
            message,
        )

    def raise_not_found(
        self,
        message: str = 'Данные не найдены',
    ) -> NoReturn:
        """Сообщит об ошибке существования данных с кодом 404."""
        raise BookingSeatsAppError(
            status.HTTP_404_NOT_FOUND,
            message,
        )

    def raise_bad_request(
        self,
        message: str = 'Идентификатор из параметров запроса не найден',
    ) -> NoReturn:
        """Сообщит об ошибке некорректного запроса с кодом 400."""
        raise BookingSeatsAppError(
            status.HTTP_400_BAD_REQUEST,
            message,
        )

    def raise_unprocessable_entity(
        self,
        message: str = 'Ошибка валидации данных',
    ) -> NoReturn:
        """Сообщит об ошибке валидации данных с кодом 422."""
        raise BookingSeatsAppError(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            message,
        )

    async def get_or_raise(
        self,
        crud: CRUDBase,
        session: AsyncSession,
        *filters: Any,
    ) -> Any:
        """Вернет объект по фильтрам.

        В противном случае сообщит об ошибке 404.
        """
        data = await crud.get(session, *filters)
        if data is None:
            self.log_warning(
                f'Объект модели {crud}, с фильтрами {filters} - не найден.',
            )
            self.raise_not_found()
        return data

    async def _find_missing_ids(
        self,
        crud: CRUDBase,
        session: AsyncSession,
        ids: set[uuid.UUID],
    ) -> set[uuid.UUID]:
        """Вернёт ID, отсутствующие в БД для указанной модели."""
        if not ids:
            return set()

        id_column = crud.model.id
        if len(ids) == 1:
            object_id = next(iter(ids))
            if await crud.exists(session, id_column == object_id):
                return set()
            return ids

        entities = await crud.get_multi(session, id_column.in_(ids))
        found_ids = {entity.id for entity in entities}
        return ids - found_ids

    async def ensure_ids_exist(
        self,
        crud: CRUDBase,
        session: AsyncSession,
        object_ids: uuid.UUID | list[uuid.UUID] | dict[uuid.UUID, uuid.UUID],
        *,
        related_crud: CRUDBase | None = None,
        message: str | None = None,
    ) -> bool:
        """Проверит наличие ID из параметров запроса в БД.

        Поддерживает:
        * один ``UUID``;
        * список ``UUID``;
        * словарь ``ключ → значение`` (например, стол → слот).

        Для словаря ``crud`` проверяет ключи, ``related_crud`` — значения.

        Возвращает ``True``, если все ID найдены.
        Иначе сообщит об ошибке 400.
        """
        primary_ids: set[uuid.UUID]
        related_ids: set[uuid.UUID] | None = None

        if isinstance(object_ids, uuid.UUID):
            primary_ids = {object_ids}
        elif isinstance(object_ids, list):
            primary_ids = set(object_ids)
        elif isinstance(object_ids, dict):
            primary_ids = set(object_ids.keys())
            related_ids = set(object_ids.values())
            if related_crud is None:
                raise ValueError(
                    'Для проверки словаря ID необходимо передать related_crud.',
                )

        missing_ids = await self._find_missing_ids(crud, session, primary_ids)
        if related_ids is not None and related_crud is not None:
            related_missing = await self._find_missing_ids(
                related_crud,
                session,
                related_ids,
            )
            missing_ids = missing_ids.union(related_missing)

        if missing_ids:
            self.raise_bad_request(
                message or f'Идентификаторы из параметров запроса не найдены: {sorted(missing_ids)}',
            )

        return True

    async def ensure_is_active(self, data: Any) -> None:
        """Проверит активность объекта.

        В противном случае сообщит об ошибке 404.
        """
        if not data.is_active:
            self.log_warning(
                f'Объект {data} - не активен.',
            )
            self.raise_unprocessable_entity()

    def ensure_belongs_to_cafe(
        self,
        data: Any,
        cafe_id: uuid.UUID,
    ) -> None:
        """Проверит принадлежность объекта кафе.

        В противном случае сообщит об ошибке 404.
        """
        if data.cafe_id != cafe_id:
            self.log_warning(
                f'Объект {data} - не принадлежит кафе {cafe_id}.',
            )
            self.raise_not_found()

    async def ensure_manager_cafe_access(
        self,
        user: User,
        cafe_id: uuid.UUID,
    ) -> None:
        """Проверит, что менеджер привязан к указанному кафе.

        В противном случае сообщит об ошибке 403.
        """
        if user.role != UserRole.MANAGER:
            return
        if user.cafe_id is None or user.cafe_id != cafe_id:
            self.log_warning(
                f'Пользователь {user.id} попытался получить доступ к кафе {cafe_id} без разрешения',
            )
            self.raise_forbidden()

    async def ensure_manajer_cafe_list_access(
        self,
        user: User,
        cafes_id: list[uuid.UUID],
        check_len: bool = False,
    ) -> None:
        """Проверяет что менеджер имеет доступ к кафе из списка."""
        if user.role != UserRole.MANAGER:
            return
        if (check_len and len(cafes_id) != 1) or (user.cafe_id not in cafes_id):
            self.log_warning(
                f'Пользователь {user.id} попытался получить доступ к кафе {cafes_id} без разрешения.',
            )
            self.raise_forbidden()

    def _child_filters_for_relationship(
        self,
        current: Any,
        relationship: Any,
    ) -> list[Any]:
        """Соберёт фильтры для дочерних записей связи ONE-TO-MANY."""
        child_filters = []
        for local_column, remote_column in relationship.local_remote_pairs:
            child_filters.append(
                remote_column == getattr(current, local_column.key),
            )
        return child_filters

    async def _deactivate_relationship_children(
        self,
        current: Any,
        relationship: Any,
        session: AsyncSession,
        deactivate_recursive: Any,
    ) -> None:
        """Деактивирует дочерние сущности связи и при необходимости обходит вложенные."""
        if relationship.direction is not RelationshipDirection.ONETOMANY:
            return

        child_model = relationship.mapper.class_
        child_mapper = sa_inspect(child_model)
        child_filters = self._child_filters_for_relationship(current, relationship)
        if not child_filters:
            return

        if 'is_active' in child_mapper.columns:
            await session.execute(
                update(child_model).where(*child_filters).values(is_active=False),
            )

        has_nested_deactivatable = any(
            nested.direction is RelationshipDirection.ONETOMANY
            and 'is_active' in sa_inspect(nested.mapper.class_).columns
            for nested in child_mapper.relationships
        )
        if not has_nested_deactivatable:
            return

        pk_columns = [getattr(child_model, column.key) for column in child_mapper.primary_key]
        child_query = select(child_model).options(load_only(*pk_columns)).where(*child_filters)
        child_entities = (await session.execute(child_query)).scalars().all()
        for child in child_entities:
            await deactivate_recursive(child)

    async def soft_delete(
        self,
        entity: Any,
        session: AsyncSession,
    ) -> Any:
        """Деактивирует объект и связанные дочерние сущности (is_active=False).

        Commit не выполняет — только подготовит изменения в сессии.
        """
        visited: set[tuple[type[Any], Any]] = set()

        async def deactivate_recursive(current: Any) -> None:
            """Рекурсивно деактивирует объект и его связанные сущности."""
            if current is None:
                return

            identity = getattr(current, 'id', id(current))
            current_key = (type(current), identity)
            if current_key in visited:
                return
            visited.add(current_key)

            current_mapper = sa_inspect(type(current))
            if 'is_active' in current_mapper.columns:
                setattr(current, 'is_active', False)
                session.add(current)

            for relationship in current_mapper.relationships:
                await self._deactivate_relationship_children(
                    current,
                    relationship,
                    session,
                    deactivate_recursive,
                )

        await deactivate_recursive(entity)
        return entity
