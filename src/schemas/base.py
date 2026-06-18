import uuid

from datetime import datetime

from typing import Optional

from pydantic import BaseModel, ConfigDict


# Не подходит для User, Action и Booking.
class BaseProjectCreate(BaseModel):
    """
    Базовая абстрактная модель для schemas сериализаторов.

    Поля: `description`.
    """

    __abstract__ = True

    description: Optional[str] = None

    model_config = ConfigDict(
        extra="forbid",
    )


# Не подходит для User и BookingTableSlot.
class BaseProjectShortInfo(BaseProjectCreate):
    """
    Базовая абсрактная модель для короткой сводки информации.

    Поля: `id`, `description`.
    """
    __abstract__ = True

    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


# Не подходит для User и Booking.
class BaseProjectInfo(BaseProjectShortInfo):
    """Базовая абстрактная модель для сериализаторов db."""

    __abstract__ = True

    is_active: bool
    create_date: datetime
    update_date: Optional[datetime]
