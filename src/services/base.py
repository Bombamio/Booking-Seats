"""Базовый миксин сервисного слоя."""

import uuid
from typing import Any, NoReturn

from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

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
        # нужно написать если подход будет использован

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
                f'Пользователь {user.id} попытался получить доступ '
                f'к кафе {cafe_id} без разрешения',
            )
            self.raise_forbidden()

    async def soft_delete(
        self,
        db_obj: Any,
        session: AsyncSession,
    ) -> Any:
        """Деактивирует объект и связанные дочерние сущности (is_active=False).

        Commit не выполняет — только подготовит изменения в сессии.
        """
        # предложение для обсуждения
