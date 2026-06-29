from pydantic import BaseModel, ConfigDict, Field


class AuthToken(BaseModel):
    """Схема токена авторизации."""

    access_token: str
    token_type: str = 'Bearer'

    model_config = ConfigDict(from_attributes=True)


class AuthData(BaseModel):
    """Схема данных для аутентификации."""

    login: str = Field(description='Логин пользователя (email или телефон)')
    password: str = Field(description='Пароль пользователя')

    model_config = ConfigDict(from_attributes=True)
