"""Схема ошибки API.

Модуль содержит единую схему для структурированного ответа об ошибке.

Схемы API:
   - `CustomError` — код и текст сообщения об ошибке.

Не использует иерархию базовых схем сущностей: наследует `BaseModel` напрямую.
"""

from pydantic import BaseModel


class CustomError(BaseModel):
    """Схема кастомной ошибки для ответа API."""

    code: int
    message: str
