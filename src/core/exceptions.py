"""Исключения приложения BookingSeats.

Модуль описывает базовые классы ошибок бизнес-логики и Celery.

Классы:
   - `BookingSeatsAppError` — ошибка с HTTP-кодом и сообщением;
   - `BookingSeatsCeleryError` — недоступность очереди фоновых задач.
"""

from fastapi import status


class BookingSeatsAppError(Exception):
    """Базовое исключение проекта."""

    def __init__(self, code: int, message: str) -> None:
        """Сохранит HTTP-код и сообщение ошибки."""
        self.code = code
        self.message = message
        super().__init__(message)


class BookingSeatsCeleryError(BookingSeatsAppError):
    """Ошибка постановки или выполнения фоновой Celery-задачи."""

    def __init__(
        self,
        message: str = 'Фоновая задача не поставлена в очередь',
    ) -> None:
        """Инициализирует ошибку недоступности очереди Celery."""
        super().__init__(status.HTTP_503_SERVICE_UNAVAILABLE, message)
