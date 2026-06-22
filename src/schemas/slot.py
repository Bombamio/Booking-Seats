import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, model_validator


class TimeSlotCreate(BaseModel):
    """Схема для создания нового временного слота."""

    start_time: datetime
    end_time: datetime

    model_config = ConfigDict(extra='forbid')

    @model_validator(mode='after')
    def check_time_order(self) -> 'TimeSlotCreate':
        """Проверяет, что `end_time` позже `start_time`."""
        if self.end_time <= self.start_time:
            raise ValueError('end_time должно быть позже start_time.')
        return self


class TimeSlotShortInfo(BaseModel):
    """Краткая информация о временном слоте."""

    id: uuid.UUID
    start_time: datetime
    end_time: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class TimeSlotInfo(TimeSlotShortInfo):
    """Полная информация о временном слоте."""

    cafe_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class TimeSlotUpdate(BaseModel):
    """Схема для обновления существующего временного слота."""

    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_active: Optional[bool] = None

    model_config = ConfigDict(extra='forbid')

    @model_validator(mode='after')
    def check_time_order(self) -> 'TimeSlotUpdate':
        """Проверяет, что `end_time` позже `start_time`, если оба заданы."""
        if (
            self.start_time is not None
            and self.end_time is not None
            and self.end_time <= self.start_time
        ):
            raise ValueError('end_time должно быть позже start_time.')
        return self
