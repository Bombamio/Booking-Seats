"""Схемы аутентификации.

Модуль описывает схемы для входа в систему и ответа с токеном доступа.

Схемы API:
   - `AuthData` — учётные данные пользователя (`login`, `password`).
   - `AuthToken` — JWT-токен и тип токена для ответа API.

Не использует иерархию `BaseCreate` / `BaseInfo`: схемы наследуют `BaseModel`
и `FromAttributesMixin` напрямую.
"""

from pydantic import BaseModel, Field

from src.schemas.base import FromAttributesMixin


class AuthToken(FromAttributesMixin, BaseModel):
    """Схема токена авторизации.

    Поля:
        access_token (str): JWT-токен доступа; обязательное.
        token_type (str): тип токена; обязательное; по умолчанию `Bearer`.
    """

    access_token: str
    token_type: str = 'Bearer'


class AuthData(FromAttributesMixin, BaseModel):
    """Схема данных для аутентификации.

    Поля:
        login (str): логин пользователя (email или телефон); обязательное.
        password (str): пароль пользователя; обязательное.
    """

    login: str = Field(description='Логин пользователя (email или телефон)')
    password: str = Field(description='Пароль пользователя')
