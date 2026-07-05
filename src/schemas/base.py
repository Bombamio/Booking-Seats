import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from src.core import constants as ct


class BaseCreate(BaseModel):
    """Базовая схема создания без общих полей модели."""

    __abstract__ = True

    model_config = ConfigDict(
        extra='forbid',
    )


class BaseShortInfo(BaseModel):
    """Базовая краткая схема без поля description."""

    id: Optional[uuid.UUID] = None

    model_config = ConfigDict(from_attributes=True)


class BaseInfo(BaseShortInfo):
    """Базовая полная схема без поля description."""

    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# Не подходит для User, Action и Booking.
class BaseProjectCreate(BaseModel):
    """Базовая абстрактная схема для создания новой модели.

    * `description` - string.
    """

    __abstract__ = True

    description: Optional[str] = Field(
        None,
        max_length=ct.MAX_DESCRIPTION_LEN,
        min_length=ct.MIN_DESCRIPTION_LEN,
    )

    model_config = ConfigDict(
        extra='forbid',
    )


# Не подходит для User и BookingTableSlot.
class BaseProjectShortInfo(BaseProjectCreate):
    """Базовая абстрактная схема с короткой сводки информации.

    * `id` - uuid;
    * `description` - string.
    """

    __abstract__ = True

    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


# Не подходит для User и Booking.
class BaseProjectInfo(BaseProjectShortInfo):
    """Базовая абстрактная схема с полной информацией о модели.

    * `id` - uuid;
    * `description` - string;
    * `is_active` - boolean;
    * `created_at` - date-time;
    * `updated_at` - date-time.
    """

    __abstract__ = True

    is_active: bool
    created_at: datetime
    updated_at: datetime
