import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.core import constants as ct
from src.models.booking import BookingStatus
from src.schemas import (
    CafeShortInfo,
    TableShortInfo,
    TimeSlotShortInfo,
    UserShortInfo,
)


class BookingTableSlot(BaseModel):
    """Базовая схема для бронирования."""

    table_id: uuid.UUID = Field(..., description='ID стола')
    slot_id: uuid.UUID = Field(..., description='ID временного слота')

    model_config = ConfigDict(
        extra='forbid',
    )


class BookingTableSlotShortInfo(BaseModel):
    """Краткая информация о бронировании."""

    table: Optional['TableShortInfo']
    slot: Optional['TimeSlotShortInfo']

    model_config = ConfigDict(from_attributes=True)


class BookingCreate(BaseModel):
    """Схема для создания нового бронирования."""

    cafe_id: uuid.UUID
    tables_slots: list[BookingTableSlot]
    guest_number: int
    note: Optional[str] = Field(
        None,
        max_length=ct.MAX_DESCRIPTION_LEN,
        description='Примечание к бронированию',
    )
    booking_date: date

    model_config = ConfigDict(
        extra='forbid',
    )

    @field_validator('booking_date')
    @classmethod
    def validate_booking_date(cls, v: date) -> date:
        """Валидация даты бронирования (не может быть в прошлом)."""
        if v < date.today():
            raise ValueError('Дата бронирования не может быть в прошлом')
        return v


class BookingUpdate(BookingCreate):
    """Схема для обновления существующего бронирования."""

    tables_slots: Optional[list[BookingTableSlot]] = None
    guest_number: Optional[int] = None
    booking_date: Optional[date] = Field(
        None,
        description='Дата бронирования',
    )
    status: Optional[BookingStatus] = Field(
        None,
        description='Статус бронирования',
    )
    note: Optional[str] = Field(
        None,
        max_length=ct.MAX_DESCRIPTION_LEN,
        description='Примечание к бронированию',
    )
    is_active: Optional[bool] = Field(
        None,
        description='Активность бронирования',
    )

    @field_validator('booking_date')
    @classmethod
    def validate_booking_date(cls, v: Optional[date]) -> Optional[date]:
        """Валидация даты бронирования (не может быть в прошлом)."""
        if v and v < date.today():
            raise ValueError('Дата бронирования не может быть в прошлом')
        return v


class BookingInfo(BaseModel):
    """Полная информация о бронировании для ответа API."""

    id: Optional[uuid.UUID] = None
    user: Optional[UserShortInfo] = None
    cafe: Optional[CafeShortInfo] = None
    tables_slots: Optional[list[BookingTableSlot]] = None
    guest_number: Optional[int] = None
    note: Optional[str] = Field(
        None,
        max_length=ct.MAX_DESCRIPTION_LEN,
        description='Примечание к бронированию',
    )
    status: Optional[BookingStatus] = None
    booking_date: Optional[date] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        """Конфигурация для модели."""

        from_attributes = True
