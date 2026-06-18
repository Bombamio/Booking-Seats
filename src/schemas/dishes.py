import uuid

from typing import Optional
from decimal import Decimal

from pydantic import Field

from schemas.base import (
    BaseProjectCreate, BaseProjectInfo
)
from core import constants as cs


class DishBase(BaseProjectCreate):
    name: Optional[str] = Field(
        None,
        max_length=cs.DISHES_MAX_NAME_LEN,
        min_length=cs.DISHES_MIN_NAME_LEN
    )
    photo_id: Optional[uuid.UUID] = Field(None)
    price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)


class DishCreate(DishBase):
    """
    Создание блюда.

    * `name` - string
    * `description` - string
    * `photo_id` - uuid
    * `price` - Decimal
    * `cafes_id`* - list integer
    """

    name: str = Field(
        ...,
        max_length=cs.DISHES_MAX_NAME_LEN,
        min_length=cs.DISHES_MIN_NAME_LEN
    )
    price: Decimal = Field(..., ge=0, decimal_places=2)
    cafes_id: list[int]


class DishInfo(BaseProjectInfo):
    """
    Полная информация о блюде.

    * `id` - int
    * `name` - string
    * `description` - string
    * `photo_id` - uuid
    * `price` - Decimal
    * `cafes` - list
    * `is_active` - boolean
    * `created_at` - date-time
    * `updated_at` - date-time
    """

    name: str
    photo_id: Optional[uuid.UUID] = Field(None)
    price: Decimal = Field(..., ge=0, decimal_places=2)
    cafes: list


class DishUpdate(DishBase):
    """
    Обновление блюда.

    * `name` - string
    * `description` - string
    * `photo_id` - uuid
    * `price` - Decimal
    * `cafes_id` - list integer
    * `is_active` - boolean
    """

    cafes_id: Optional[list[int]] = None
    is_active: Optional[bool] = None
