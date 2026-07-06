import uuid
from datetime import date
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, PositiveInt, field_validator, model_validator

from src.core import constants as ct
from src.models import BookingStatus
from src.schemas.base import BaseCreate, BaseInfo
from src.schemas.cafe import CafeShortInfo
from src.schemas.dish import DishInfo
from src.schemas.slot import TimeSlotShortInfo
from src.schemas.table import TableShortInfo
from src.schemas.user import UserShortInfo


class BookingTableSlot(BaseCreate):
    """Базовая схема для бронирования."""

    table_id: uuid.UUID
    slot_id: uuid.UUID


class BookingDishCreate(BaseCreate):
    """Схема блюда в предзаказе бронирования."""

    dish_id: uuid.UUID
    quantity: PositiveInt


class BookingDishInfo(BaseModel):
    """Информация о блюде в предзаказе бронирования."""

    dish: DishInfo
    quantity: PositiveInt

    model_config = ConfigDict(from_attributes=True)


class BookingTableSlotShortInfo(BaseModel):
    """Краткая информация о бронировании."""

    table: TableShortInfo
    slot: TimeSlotShortInfo

    model_config = ConfigDict(from_attributes=True)


class _BookingBase(BaseModel):
    """Миксин с атрибутами бронирования."""

    preordered_dishes: Optional[list[BookingDishCreate]] = Field(default_factory=list)
    guest_number: Optional[PositiveInt] = None
    booking_date: Optional[date] = None
    note: Optional[str] = Field(
        None,
        max_length=ct.MAX_DESCRIPTION_LEN,
        description='Примечание к бронированию',
    )

    @field_validator('booking_date', check_fields=False)
    @classmethod
    def validate_booking_date(cls, v: Optional[date]) -> Optional[date]:
        """Валидация даты бронирования (не может быть в прошлом)."""
        if v and v < date.today():
            raise ValueError('Дата бронирования не может быть в прошлом')
        return v


class BookingCreate(_BookingBase, BaseCreate):
    """Схема для создания нового бронирования."""

    cafe_id: uuid.UUID
    tables_slots: list[BookingTableSlot] = Field(min_length=1)
    guest_number: PositiveInt
    booking_date: date


class BookingUpdate(_BookingBase, BaseCreate):
    """Схема для обновления существующего бронирования."""

    tables_slots: Optional[list[BookingTableSlot]] = Field(None)
    status: Optional[BookingStatus] = Field(
        None,
        description='Статус бронирования',
    )
    is_active: Optional[bool] = Field(None)

    @model_validator(mode='before')
    @classmethod
    def reject_null(cls, values: Any) -> Any:
        """Сообщит об ошибке, если в полях запроса передано значение Null."""
        for field in cls.model_fields:
            if field in values and values[field] is None:
                raise ValueError(f'Поле "{field}" не может быть пустым.')
        return values


class BookingInfo(_BookingBase, BaseInfo):
    """Полная информация о бронировании для ответа API."""

    user: UserShortInfo
    cafe: CafeShortInfo
    tables_slots: list[BookingTableSlotShortInfo]
    preordered_dishes: list[BookingDishInfo] = Field(default_factory=list)
    status: BookingStatus
