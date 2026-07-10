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
from src.models import User, UserRole


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

    def raise_unauthorized(
        self,
        message: str = 'Неавторизированный пользователь',
    ) -> NoReturn:
        """Сообщит об ошибке авторизации с кодом 401."""
        raise BookingSeatsAppError(
            status.HTTP_401_UNAUTHORIZED,
            message,
        )

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

    def raise_unprocessable_entity(
        self,
        message: str = 'Ошибка валидации данных',
    ) -> NoReturn:
        """Сообщит об ошибке валидации данных с кодом 422."""
        raise BookingSeatsAppError(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            message,
        )

    async def ensure_exists(
        self,
        crud: Any,
        session: AsyncSession,
        *filters: Any,
    ) -> None:
        """Проверит существование объекта по фильтрам.

        В противном случае сообщит об ошибке 404.
        """
        if not await crud.exists(session, *filters):
            self.log_warning(
                f'Объект модели {crud}, с фильтрами {filters} - не найден.',
            )
            self.raise_not_found()

    async def get_or_raise(
        self,
        crud: Any,
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

    async def ensure_cafes_len(
        self,
        cafes: Any,
        cafes_id: list[uuid.UUID],
    ) -> None:
        """Проверит, что все переданные ID кафе существуют."""
        if len(cafes) != len(cafes_id):
            self.log_warning(f'Задано {len(cafes_id)} кафе, вернулось - {len(cafes)}.')
            self.raise_unprocessable_entity()

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
