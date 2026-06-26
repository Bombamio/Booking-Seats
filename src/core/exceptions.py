class BookingSeatsAppError(Exception):
    """Базовое исключение проекта."""

    def __init__(self, code: int, message: str) -> None:
        """Инициализирует исключение с кодом и сообщением."""
        self.code = code
        self.message = message
        super().__init__(message)
