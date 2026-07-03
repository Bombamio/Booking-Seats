import re
import uuid
from datetime import datetime
from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.core import constants as ct


class UserRole(StrEnum):
    """Роли пользователей."""

    ADMIN = 'ADMIN'
    MANAGER = 'MANAGER'
    USER = 'USER'


class UserBase(BaseModel):
    """Базовая схема пользователя."""

    username: str = Field(min_length=ct.MIN_USERNAME_LEN, max_length=ct.MAX_USERNAME_LEN)
    email: Optional[str] = Field(default=None, max_length=ct.MAX_EMAIL_LEN)
    phone: Optional[str] = Field(default=None, max_length=ct.MAX_PHONE_LEN)
    tg_id: Optional[str] = Field(max_length=ct.MAX_TG_ID_LEN)

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, value: str) -> str:
        """Валидация номера телефона."""
        regex_for_phone = r'^\+\d{1,15}$'
        if not re.match(regex_for_phone, value):
            raise ValueError('Номер телефона должен начинаться с "+" исодержать от 1 до 15 цифр')
        return value

    @field_validator('email')
    @classmethod
    def validate_email(cls, value: str) -> str:
        """Валидация email."""
        regex_for_email = r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(regex_for_email, value):
            raise ValueError('Неверный формат email')
        return value


class UserCreate(UserBase):
    """Схема создания пользователя."""

    password: str = Field(min_length=ct.MIN_PASSWORD_LEN, max_length=ct.MAX_PASSWORD_LEN)

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='after')
    def validate_contact_info(self) -> 'UserCreate':
        """Валидация: хотя бы одно из полей email/phone заполнено."""
        email = self.email.strip() if isinstance(self.email, str) else None
        phone = self.phone.strip() if isinstance(self.phone, str) else None

        if not email and not phone:
            raise ValueError('Хотя бы одно из полей email/phone должно быть заполнено.')

        return self


class UserInfo(UserBase):
    """Схема информации о пользователе."""

    id: int
    role: UserRole
    cafe_id: uuid.UUID = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserShortInfo(UserBase):
    """Схема краткой информации о пользователе."""

    id: int

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """Схема обнолвения информации о пользователе."""

    username: Optional[str] = Field(min_length=ct.MIN_USERNAME_LEN, max_length=ct.MAX_USERNAME_LEN)
    email: Optional[str] = Field(max_length=ct.MAX_EMAIL_LEN)
    phone: Optional[str] = Field(max_length=ct.MAX_PHONE_LEN)
    tg_id: Optional[str] = Field(max_length=ct.MAX_TG_ID_LEN)
    role: Optional[UserRole] = Field(default=UserRole.USER)
    cafe_id: Optional[uuid.UUID] = Field(default=None)
    password: Optional[str] = Field(min_length=ct.MIN_PASSWORD_LEN, max_length=ct.MAX_PASSWORD_LEN)

    @model_validator(mode='after')
    def validate_cafe_id(self) -> 'UserUpdate':
        """Валидация кафе для роли пользователя: менеджер."""
        if self.role != UserRole.MANAGER and self.cafe_id is not None:
            raise ValueError('Кафе может быть назначено только менеджерам(cafe_id должно быть None).')

        return self
