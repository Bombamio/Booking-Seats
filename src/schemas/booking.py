import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.core import constants as ct
from src.models.booking import BookingStatus
from src.schemas import (
    CafeShortInfo,
    SlotInfo,
    TableShortInfo,
    TimeSlotShortInfo,
    UserShortInfo,
)


# ERROR: К твоим schemas не подходит уже созданные базовые классы, там есть
# лишнее для тебя поле description.
class BookingTableSlot(BaseModel):
    """Базовая схема для бронирования."""

    # TODO: Нужны тольько 2 поля: table_id и slot_id.

    # user_id: uuid.UUID = Field(..., description='ID пользователя')
    # cafe_id: uuid.UUID = Field(..., description='ID кафе')
    table_id: uuid.UUID = Field(..., description='ID стола')
    slot_id: uuid.UUID = Field(..., description='ID временного слота')
    # booking_date: date = Field(..., description='Дата бронирования')
    # note: Optional[str] = Field(
    #     None,
    #     max_length=ct.MAX_DESCRIPTION_LEN,
    #     description='Примечание к бронированию',
    # )

    model_config = ConfigDict(
        extra='forbid',
    )


class BookingTableSlotShortInfo(BaseModel):
    """Краткая информация о бронировании."""

    # user_id: uuid.UUID
    # cafe_id: uuid.UUID
    # table_id: uuid.UUID
    # slot_id: uuid.UUID
    # booking_date: date
    # status: BookingStatus
    # note: Optional[str] = None

    # TODO: Если я правильно понял, то этот класс должен выглядить так:
    table: Optional['TableShortInfo']
    slot: Optional['TimeSlotShortInfo']
    # А поля выше - лишние.

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

    # Не нужное поле.
    # status: BookingStatus = Field(
    #     default=BookingStatus.PENDING,
    #     description='Статус бронирования',
    # )

    @field_validator('booking_date')
    @classmethod
    def validate_booking_date(cls, v: date) -> date:
        """Валидация даты бронирования (не может быть в прошлом)."""
        if v < date.today():
            raise ValueError('Дата бронирования не может быть в прошлом')
        return v


class BookingUpdate(BookingCreate):
    """Схема для обновления существующего бронирования."""

    # Лишние поля.
    # user_id: Optional[uuid.UUID] = Field(
    #     None,
    #     description='ID пользователя',
    # )
    # cafe_id: Optional[uuid.UUID] = Field(
    #     None,
    #     description='ID кафе',
    # )
    # table_id: Optional[uuid.UUID] = Field(
    #     None,
    #     description='ID стола',
    # )
    # slot_id: Optional[uuid.UUID] = Field(
    #     None,
    #     description='ID временного слота',
    # )

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

    # Лишние поля.
    # user_id: uuid.UUID
    # cafe_id: uuid.UUID
    # table_id: uuid.UUID
    # slot_id: uuid.UUID

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


# Походу вспомогательный класс, но я не помню где ты его использовал.
class BookingDetailedInfo(BookingInfo):
    """Расширенная информация о бронировании с вложенными объектами."""

    user: Optional['UserShortInfo'] = None
    cafe: Optional['CafeShortInfo'] = None
    table: Optional['TableShortInfo'] = None
    slot: Optional['SlotInfo'] = None
