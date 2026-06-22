"""Импорты."""
import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import Field, field_validator

from src.core import constants as ct
from src.models.booking import BookingStatus
from src.schemas import (
    BaseProjectCreate,
    BaseProjectInfo,
    BaseProjectShortInfo,
    CafeShortInfo,
    SlotInfo,
    TableShortInfo,
)
from src.schemas.user import UserShortInfo


class BookingTableSlot(BaseProjectCreate):
    """Базовая схема для бронирования."""

    user_id: uuid.UUID = Field(..., description='ID пользователя')
    cafe_id: uuid.UUID = Field(..., description='ID кафе')
    table_id: uuid.UUID = Field(..., description='ID стола')
    slot_id: uuid.UUID = Field(..., description='ID временного слота')
    booking_date: date = Field(..., description='Дата бронирования')
    note: Optional[str] = Field(
        None,
        max_length=ct.MAX_DESCRIPTION_LEN,
        description='Примечание к бронированию',
    )


class BookingTableSlotShortInfo(BaseProjectShortInfo):
    """Краткая информация о бронировании."""

    user_id: uuid.UUID
    cafe_id: uuid.UUID
    table_id: uuid.UUID
    slot_id: uuid.UUID
    booking_date: date
    status: BookingStatus
    note: Optional[str] = None


class BookingCreate(BookingTableSlot):
    """Схема для создания нового бронирования."""

    status: BookingStatus = Field(
        default=BookingStatus.PENDING,
        description='Статус бронирования',
    )

    @field_validator('booking_date')
    @classmethod
    def validate_booking_date(cls, v: date) -> date:
        """Валидация даты бронирования (не может быть в прошлом)."""
        if v < date.today():
            raise ValueError('Дата бронирования не может быть в прошлом')
        return v


class BookingUpdate(BaseProjectCreate):
    """Схема для обновления существующего бронирования."""

    user_id: Optional[uuid.UUID] = Field(
        None,
        description='ID пользователя'
    )
    cafe_id: Optional[uuid.UUID] = Field(
        None,
        description='ID кафе'
    )
    table_id: Optional[uuid.UUID] = Field(
        None,
        description='ID стола'
    )
    slot_id: Optional[uuid.UUID] = Field(
        None,
        description='ID временного слота'
    )
    booking_date: Optional[date] = Field(
        None,
        description='Дата бронирования'
    )
    status: Optional[BookingStatus] = Field(
        None,
        description='Статус бронирования'
    )
    note: Optional[str] = Field(
        None,
        max_length=ct.MAX_DESCRIPTION_LEN,
        description='Примечание к бронированию',
    )
    is_active: Optional[bool] = Field(
        None,
        description='Активность бронирования'
    )

    @field_validator('booking_date')
    @classmethod
    def validate_booking_date(cls, v: Optional[date]) -> Optional[date]:
        """Валидация даты бронирования (не может быть в прошлом)."""
        if v and v < date.today():
            raise ValueError('Дата бронирования не может быть в прошлом')
        return v


class BookingInfo(BaseProjectInfo):
    """Полная информация о бронировании для ответа API."""

    user_id: uuid.UUID
    cafe_id: uuid.UUID
    table_id: uuid.UUID
    slot_id: uuid.UUID
    booking_date: date
    status: BookingStatus
    note: Optional[str] = None

    class Config:
        """Конфигурация для модели."""

        from_attributes = True


class BookingDetailedInfo(BookingInfo):
    """Расширенная информация о бронировании с вложенными объектами."""

    user: Optional['UserShortInfo'] = None
    cafe: Optional['CafeShortInfo'] = None
    table: Optional['TableShortInfo'] = None
    slot: Optional['SlotInfo'] = None
