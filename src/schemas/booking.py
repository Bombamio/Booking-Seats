"""Схемы бронирования.

Модуль описывает входные и выходные схемы для создания и управления бронированиями.

Локальные миксины:
   - `BookingBaseMixin` — основные поля бронирования и вложенные списки.
   - `BookingDateValidationMixin` — дата бронирования не может быть в прошлом.
   - `BookingTableSlotMixin` / `BookingDishMixin` — вложенные сущности в запросе и ответе.

Схемы API:
   - `BookingCreate` — создание бронирования с обязательными полями и `cafe_id`.
   - `BookingUpdate` — частичное обновление; переданные NOT NULL-поля не принимают `null`.
   - `BookingInfo` — полный ответ API с пользователем, кафе, столами, блюдами и статусом.

Наследование:
   - входные схемы — `BaseCreate` / `BaseUpdate` (без `description`);
   - выходная схема — `BaseInfo`;
   - вложенные схемы — `BaseCreate`, `BaseShortInfo`, `BaseInfo`.

Общие правила наследования и базовые миксины — в `src/schemas/base.py`.
"""

import uuid
from datetime import date
from typing import ClassVar

from pydantic import BaseModel, Field, PositiveInt, field_validator

from src.core import constants as ct
from src.models import BookingStatus
from src.schemas.base import BaseCreate, BaseInfo, BaseUpdate, FromAttributesMixin
from src.schemas.cafe import CafeShortInfo
from src.schemas.dish import DishInfo
from src.schemas.slot import TimeSlotShortInfo
from src.schemas.table import TableShortInfo
from src.schemas.user import UserShortInfo


class BookingTableSlotMixin:
    """Миксин с атрибутами пары столик-слот бронирования."""

    table_id: uuid.UUID
    slot_id: uuid.UUID


class BookingTableSlotCreate(BookingTableSlotMixin, BaseCreate):
    """Базовая схема для бронирования."""


class BookingTableSlotShortInfo(FromAttributesMixin, BaseModel):
    """Краткая информация о паре столик-слот в бронировании.

    Поля:
        table (TableShortInfo): столик.
        slot (TimeSlotShortInfo): временной слот.
    """

    table: TableShortInfo
    slot: TimeSlotShortInfo


class BookingDishMixin:
    """Миксин с атрибутами блюда в предзаказе бронирования."""

    dish_id: uuid.UUID
    quantity: PositiveInt


class BookingDishCreate(BookingDishMixin, BaseCreate):
    """Схема блюда в предзаказе бронирования.

    Поля (включая унаследованные):
        dish_id (UUID): идентификатор блюда; обязательное.
        quantity (PositiveInt): количество порций; обязательное.
    """


class BookingDishInfo(FromAttributesMixin, BaseModel):
    """Информация о блюде в предзаказе бронирования.

    Поля:
        dish (DishInfo): информация о блюде.
        quantity (PositiveInt): количество порций.
    """

    dish: DishInfo
    quantity: PositiveInt


class BookingBaseMixin:
    """Миксин с атрибутами бронирования.

    Поля:
        booking_date (date): дата бронирования; обязательное.
        guest_number (PositiveInt): количество гостей; обязательное.
        note (str | None): примечание; необязательное.
        tables_slots (list[BookingTableSlotCreate]): столики и слоты; обязательное.
        pre_ordered_dishes (list[BookingDishCreate] | None): предзаказ блюд; необязательное.
    """

    booking_date: date = Field(description='Дата бронирования')
    guest_number: PositiveInt = Field(description='Количество гостей')
    note: str | None = Field(
        None,
        max_length=ct.MAX_DESCRIPTION_LEN,
        description='Примечание к бронированию',
    )
    tables_slots: list[BookingTableSlotCreate] = Field(min_length=ct.MIN_TABLE_SLOT_COUNT)
    pre_ordered_dishes: list[BookingDishCreate] | None = Field(
        default_factory=list,
        description='Список блюд, предварительно заказанных клиентом',
    )


class BookingDateValidationMixin:
    """Миксин с валидацией даты бронирования."""

    @field_validator('booking_date', check_fields=False)
    @classmethod
    def validate_booking_date(cls, booking_date: date | None) -> date | None:
        """Валидация даты бронирования (не может быть в прошлом)."""
        if booking_date and booking_date < date.today():
            raise ValueError('Дата бронирования не может быть в прошлом')
        return booking_date


class BookingCreate(BookingDateValidationMixin, BookingBaseMixin, BaseCreate):
    """Схема для создания нового бронирования.

    Поля (включая унаследованные):
        booking_date (date): дата бронирования; обязательное.
        guest_number (PositiveInt): количество гостей; обязательное.
        note (str | None): примечание; необязательное.
        tables_slots (list[BookingTableSlotCreate]): столики и слоты; обязательное.
        pre_ordered_dishes (list[BookingDishCreate] | None): предзаказ блюд; необязательное.
        cafe_id (UUID): идентификатор кафе; обязательное.
    """

    cafe_id: uuid.UUID


class BookingUpdate(BookingDateValidationMixin, BookingBaseMixin, BaseUpdate):
    """Схема для обновления существующего бронирования.

    Поля (включая унаследованные):
        booking_date (date | None): дата бронирования; необязательное; явный null запрещён.
        guest_number (PositiveInt | None): количество гостей; необязательное; явный null запрещён.
        note (str | None): примечание; необязательное.
        tables_slots (list[BookingTableSlotCreate] | None): столики и слоты; необязательное;
        явный null запрещён.
        pre_ordered_dishes (list[BookingDishCreate] | None): предзаказ блюд; необязательное.
        status (BookingStatus | None): статус бронирования; необязательное; явный null запрещён.
        is_active (bool | None): признак активности; необязательное; явный null запрещён.
    """

    booking_date: date | None = Field(None, description='Дата бронирования')
    guest_number: PositiveInt | None = Field(None, description='Количество гостей')
    tables_slots: list[BookingTableSlotCreate] | None = None
    status: BookingStatus | None = Field(
        None,
        description='Статус бронирования',
    )

    _not_null_fields: ClassVar[set[str]] = {
        'booking_date',
        'guest_number',
        'tables_slots',
        'status',
        'is_active',
    }


class BookingInfo(BookingBaseMixin, BaseInfo):
    """Полная информация о бронировании для ответа API.

    Поля (включая унаследованные):
        booking_date (date): дата бронирования.
        guest_number (PositiveInt): количество гостей.
        note (str | None): примечание.
        id (UUID): идентификатор бронирования.
        is_active (bool | None): признак активности.
        created_at (datetime): дата создания.
        updated_at (datetime): дата обновления.
        user (UserShortInfo): пользователь.
        cafe (CafeShortInfo): кафе.
        tables_slots (list[BookingTableSlotShortInfo]): столики и слоты.
        preordered_dishes (list[BookingDishInfo]): предзаказ блюд.
        status (BookingStatus): статус бронирования.
    """

    user: UserShortInfo
    cafe: CafeShortInfo
    tables_slots: list[BookingTableSlotShortInfo]
    preordered_dishes: list[BookingDishInfo] = Field(default_factory=list)
    status: BookingStatus
