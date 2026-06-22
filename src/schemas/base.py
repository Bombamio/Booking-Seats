import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from src.core import constants as ct


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

    * `id` - int;
    * `description` - string.
    """

    __abstract__ = True

    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


# Не подходит для User и Booking.
class BaseProjectInfo(BaseProjectShortInfo):
    """Базовая абстрактная схема с полной информацией о модели.

    * `id` - int;
    * `description` - string;
    * `is_active` - boolean;
    * `created_at` - date-time;
    * `updated_at` - date-time.
    """

    __abstract__ = True

    is_active: bool
    created_at: datetime
    updated_at: datetime
