"""Базовый миксин сервисного слоя."""

import uuid
from typing import Any, NoReturn

from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import BookingSeatsAppError
from src.core.logger import bookingseats_logger
from src.models import User


class BaseService:
    """Базовый миксин сервисного слоя.

    Предложение одного из возможных вариантов реализации.
    Должен быть скорректирован позднее.
    Приведены методы, использование которых предполагается на примере сервиса
    для Table
    методы логирования и ошибки доступа реализованы как общие для почти всех сервисов

    """

    def log_info(self, message: str) -> None:
        """Запишет информационное сообщение в лог."""
        bookingseats_logger.info(message)

    def log_warning(self, message: str) -> None:
        """Запишет предупреждение в лог."""
        bookingseats_logger.warning(message)

    def raise_forbidden(self, message: str = 'Доступ запрещен') -> NoReturn:
        """Сообщит об ошибке доступа с кодом 403."""
        raise BookingSeatsAppError(status.HTTP_403_FORBIDDEN, message)

    async def ensure_exists(
        self,
        crud: Any,
        session: AsyncSession,
        *filters: Any,
    ) -> None:
        """Проверит существование объекта по фильтрам и сообщит об ошибке 404."""
        # нужно дописать если подхд будет принят

    async def get_or_raise(
        self,
        crud: Any,
        session: AsyncSession,
        *filters: Any,
    ) -> Any:
        """Вернет объект по фильтрам или сообщит об ошибке 404."""
        # нужно написать если подход будет использован

    def ensure_is_active(self, data: Any) -> None:
        """Проверит активность объекта и сообщит об ошибке 404, если неактивен."""
        # нужно написать если подход будет использован

    def ensure_belongs_to_cafe(
        self,
        data: Any,
        cafe_id: uuid.UUID,
    ) -> None:
        """Проверит принадлежность объекта кафе и сообщит об ошибке 404."""
        # нужно написать если подход будет использован

    async def ensure_manager_cafe_access(
        self,
        user: User,
        cafe_id: uuid.UUID,
        session: AsyncSession,
    ) -> None:
        """Проверит, что менеджер привязан к указанному кафе."""
        # нужно написать если подход будет использован

    async def soft_delete(
        self,
        db_obj: Any,
        session: AsyncSession,
    ) -> Any:
        """Деактивирует объект и связанные дочерние сущности (is_active=False).

        Commit не выполняет — только подготовит изменения в сессии.
        """
        # предложение для обсуждения
