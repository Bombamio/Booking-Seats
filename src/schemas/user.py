"""Схемы пользователя.

Модуль описывает входные и выходные схемы для управления пользователями системы.

Локальные миксины:
   - `UserBaseMixin` — имя, контакты и Telegram ID; форматы email и телефона
     проверяются через `pattern` из констант.

Схемы API:
   - `UserCreate` — регистрация пользователя с обязательным паролем;
     требуется хотя бы одно из полей `email` / `phone`.
   - `UserUpdate` — частичное обновление; `cafe_id` допустимо только для роли `MANAGER`;
     контакты валидируются только при явной передаче `email` / `phone`.
   - `UserShortInfo` — краткая информация для вложенных ответов.
   - `UserInfo` — полный ответ API с ролью и привязкой к кафе.

Наследование:
   - входные схемы — `BaseCreate` / `BaseUpdate` (без `description`);
   - выходные схемы — `BaseShortInfo` / `BaseInfo`.

Общие правила наследования и базовые миксины — в `src/schemas/base.py`.
"""

import uuid
from typing import ClassVar

from pydantic import Field, model_validator

from src.core import constants as ct
from src.models.user import UserRole
from src.schemas.base import BaseCreate, BaseInfo, BaseShortInfo, BaseUpdate


class UserBaseMixin:
    """Миксин с атрибутами пользователя.

    Поля:
        username (str): имя пользователя; обязательное.
        email (str | None): адрес электронной почты; необязательное.
        phone (str | None): номер телефона; необязательное.
        tg_id (str | None): идентификатор Telegram; необязательное.
    """

    username: str = Field(min_length=ct.MIN_USERNAME_LEN, max_length=ct.MAX_USERNAME_LEN)
    email: str | None = Field(
        None,
        max_length=ct.MAX_EMAIL_LEN,
        pattern=ct.USER_EMAIL_PATTERN,
        example='user@example.com',
    )
    phone: str | None = Field(
        None,
        max_length=ct.MAX_PHONE_LEN,
        pattern=ct.USER_PHONE_PATTERN,
        example='+79912223344',
    )
    tg_id: str | None = Field(None, max_length=ct.MAX_TG_ID_LEN)


class UserCreate(UserBaseMixin, BaseCreate):
    """Схема создания пользователя.

    Поля (включая унаследованные):
        username (str): имя пользователя; обязательное.
        email (str | None): адрес электронной почты; необязательное.
        phone (str | None): номер телефона; необязательное.
        tg_id (str | None): идентификатор Telegram; необязательное.
        password (str): пароль; обязательное.
    """

    password: str = Field(min_length=ct.MIN_PASSWORD_LEN, max_length=ct.MAX_PASSWORD_LEN)

    @model_validator(mode='after')
    def validate_contact_info(self) -> 'UserCreate':
        """Валидация: хотя бы одно из полей email/phone заполнено."""
        email = self.email.strip() if isinstance(self.email, str) else None
        phone = self.phone.strip() if isinstance(self.phone, str) else None

        if not email and not phone:
            raise ValueError('Хотя бы одно из полей email/phone должно быть заполнено.')

        return self


class UserUpdate(UserBaseMixin, BaseUpdate):
    """Схема обновления информации о пользователе.

    Поля (включая унаследованные):
        username (str | None): имя пользователя; необязательное; явный null запрещён.
        email (str | None): адрес электронной почты; необязательное.
        phone (str | None): номер телефона; необязательное.
        tg_id (str | None): идентификатор Telegram; необязательное.
        password (str | None): пароль; необязательное; явный null запрещён.
        role (UserRole): роль пользователя; необязательное; явный null запрещён.
        cafe_id (UUID | None): идентификатор кафе; необязательное; явный null запрещён.
        is_active (bool | None): признак активности; необязательное; явный null запрещён.
    """

    username: str | None = Field(None, min_length=ct.MIN_USERNAME_LEN, max_length=ct.MAX_USERNAME_LEN)
    password: str | None = Field(None, min_length=ct.MIN_PASSWORD_LEN, max_length=ct.MAX_PASSWORD_LEN)
    role: UserRole = Field(default=UserRole.USER)
    cafe_id: uuid.UUID | None = Field(default=None)

    _not_null_fields: ClassVar[set[str]] = {
        'username',
        'password',
        'role',
        'cafe_id',
        'is_active',
    }

    @model_validator(mode='after')
    def validate_contact_info(self) -> 'UserUpdate':
        """Валидация контактов только при явной передаче email/phone."""
        contact_fields = {'email', 'phone'}
        if not contact_fields & self.model_fields_set:
            return self

        email = self.email.strip() if isinstance(self.email, str) else None
        phone = self.phone.strip() if isinstance(self.phone, str) else None

        if not email and not phone:
            raise ValueError('Хотя бы одно из полей email/phone должно быть заполнено.')

        return self

    @model_validator(mode='after')
    def validate_cafe_id(self) -> 'UserUpdate':
        """Валидация кафе для роли пользователя: менеджер."""
        if self.role != UserRole.MANAGER and self.cafe_id is not None:
            raise ValueError('Кафе может быть назначено только менеджерам (cafe_id должно быть None).')
        return self


class UserShortInfo(UserBaseMixin, BaseShortInfo):
    """Схема краткой информации о пользователе.

    Поля (включая унаследованные):
        username (str): имя пользователя.
        email (str | None): адрес электронной почты.
        phone (str | None): номер телефона.
        tg_id (str | None): идентификатор Telegram.
        id (UUID): идентификатор пользователя.
        is_active (bool | None): признак активности.
    """


class UserInfo(UserBaseMixin, BaseInfo):
    """Схема краткой информации о пользователе.

    Поля (включая унаследованные):
        username (str): имя пользователя.
        email (str | None): адрес электронной почты.
        phone (str | None): номер телефона.
        tg_id (str | None): идентификатор Telegram.
        id (UUID): идентификатор пользователя.
        is_active (bool | None): признак активности.
        created_at (datetime): дата создания.
        updated_at (datetime): дата обновления.
        role (UserRole): роль пользователя.
        cafe_id (UUID | None): идентификатор кафе.
    """

    role: UserRole
    cafe_id: uuid.UUID | None = None
