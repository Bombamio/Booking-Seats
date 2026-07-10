from fastapi import status


class BookingSeatsAppError(Exception):
    """Базовое исключение проекта."""

    def __init__(self, code: int, message: str) -> None:
        """Инициализирует исключение с кодом и сообщением."""
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
