"""Схемы блюда.

Модуль описывает входные и выходные схемы для управления блюдами и их привязкой к кафе.

Локальные миксины:
   - `DishBaseMixin` — название и цена блюда.

Схемы API:
   - `DishCreate` — создание блюда с привязкой к одному или нескольким кафе.
   - `DishUpdate` — частичное обновление; `name`, `price` и `cafes_id` не принимают `null`.
   - `DishInfo` — полный ответ API со списком связанных кафе.

Наследование:
   - входные схемы — `BaseDescriptionCreate` / `BaseDescriptionUpdate`;
   - выходная схема — `BaseDescriptionInfo`;
   - `PhotoIdMixin` — опциональное изображение блюда.

Общие правила наследования и базовые миксины — в `src/schemas/base.py`.
"""

import uuid

from pydantic import Field, PositiveInt

from src.core import constants as ct
from src.schemas.base import (
    BaseDescriptionCreate,
    BaseDescriptionInfo,
    BaseDescriptionUpdate,
    PhotoIdMixin,
)
from src.schemas.cafe import CafeShortInfo


class DishBaseMixin:
    """Миксин с атрибутами блюда."""

    name: str = Field(max_length=ct.MAX_NAME_LEN)
    price: PositiveInt


class DishCreate(DishBaseMixin, PhotoIdMixin, BaseDescriptionCreate):
    """Схема для создание нового блюда.

    Поля (включая унаследованные):
        description (str | None): описание блюда; необязательное.
        name (str): название блюда; обязательное.
        price (PositiveInt): цена блюда; обязательное.
        photo_id (UUID | None): идентификатор изображения; необязательное.
        cafes_id (list[UUID]): идентификаторы кафе; обязательное.
    """

    cafes_id: list[uuid.UUID]


class DishUpdate(DishBaseMixin, PhotoIdMixin, BaseDescriptionUpdate):
    """Схема для обновления существующего блюда.

    Поля (включая унаследованные):
        description (str | None): описание блюда; необязательное.
        name (str | None): название блюда; необязательное; явный null запрещён.
        price (PositiveInt | None): цена блюда; необязательное; явный null запрещён.
        photo_id (UUID | None): идентификатор изображения; необязательное.
        is_active (bool | None): признак активности; необязательное; явный null запрещён.
        cafes_id (list[UUID] | None): идентификаторы кафе; необязательное; явный null запрещён.
    """

    name: str | None = Field(None, max_length=ct.MAX_NAME_LEN)
    price: PositiveInt | None = Field(None)
    cafes_id: list[uuid.UUID] | None = None

    _not_null_fields: set[str] = {'name', 'price', 'cafes_id', 'is_active'}


class DishInfo(DishBaseMixin, PhotoIdMixin, BaseDescriptionInfo):
    """Схема с полной информацией о блюде.

    Поля (включая унаследованные):
        description (str | None): описание блюда.
        is_active (bool | None): признак активности.
        id (UUID): идентификатор блюда.
        created_at (datetime): дата создания.
        updated_at (datetime): дата обновления.
        name (str): название блюда.
        price (PositiveInt): цена блюда.
        photo_id (UUID | None): идентификатор изображения.
        cafes (list[CafeShortInfo]): связанные кафе.
    """

    cafes: list[CafeShortInfo]
