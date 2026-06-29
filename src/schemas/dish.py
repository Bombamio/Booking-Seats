import uuid
from typing import Optional

from pydantic import Field

from src.core import constants as ct
from src.schemas import (
    BaseProjectCreate,
    BaseProjectInfo,
    CafeShortInfo,
)


class DishBase(BaseProjectCreate):
    """Базовая схема для Dish.

    * `name` - string;
    * `description` - string;
    * `photo_id` - uuid;
    * `price` - int.
    """

    name: Optional[str] = Field(
        None,
        max_length=ct.MAX_NAME_LEN,
        min_length=ct.MIN_NAME_LEN,
    )
    photo_id: Optional[uuid.UUID] = None
    price: Optional[int] = Field(
        None,
        ge=0,
    )


class DishCreate(DishBase):
    """Схема для создание нового блюда.

    * `name` - string;
    * `description` - string;
    * `photo_id` - uuid;
    * `price` - int;
    * `cafes_id` - list uuid.
    """

    name: str = Field(
        ...,
        max_length=ct.MAX_NAME_LEN,
        min_length=ct.MIN_NAME_LEN,
    )
    price: int = Field(
        ...,
        ge=0,
    )
    cafes_id: list[uuid.UUID]


class DishInfo(BaseProjectInfo):
    """Схема с полной информацией о блюде.

    * `id` - int;
    * `name` - string;
    * `description` - string;
    * `photo_id` - uuid;
    * `price` - int;
    * `cafes` - list;
    * `is_active` - boolean;
    * `created_at` - date-time;
    * `updated_at` - date-time.
    """

    name: str = Field(
        ...,
        max_length=ct.MAX_NAME_LEN,
        min_length=ct.MIN_NAME_LEN,
    )
    photo_id: Optional[uuid.UUID] = None
    price: int = Field(
        ...,
        ge=0,
    )
    cafes: list[CafeShortInfo]


class DishUpdate(DishBase):
    """Схема для обновления существующего блюда.

    * `name` - string;
    * `description` - string;
    * `photo_id` - uuid;
    * `price` - int;
    * `cafes_id` - list uuid.
    * `is_active` - boolean.
    """

    cafes_id: Optional[list[uuid.UUID]] = None
    is_active: Optional[bool] = None
