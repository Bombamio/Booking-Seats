from pydantic import BaseModel


class CustomError(BaseModel):
    """Схема кастомной ошибки для ответа API."""

    code: int
    message: str
