import uuid
from datetime import datetime
from typing import Optional

from pydantic import model_validator

from src.schemas.base import BaseProjectCreate, BaseProjectShortInfo


class TimeSlotCreate(BaseProjectCreate):
    """Схема для создания нового временного слота."""

    start_time: datetime
    end_time: datetime

    @model_validator(mode='after')
    def check_time_order(self) -> 'TimeSlotCreate':
        """Проверяет, что `end_time` позже `start_time`."""
        if self.end_time <= self.start_time:
            raise ValueError('end_time должно быть позже start_time.')
        return self


class TimeSlotShortInfo(BaseProjectShortInfo):
    """Краткая информация о временном слоте."""

    start_time: datetime
    end_time: datetime
    is_active: bool


class TimeSlotInfo(TimeSlotShortInfo):
    """Полная информация о временном слоте."""

    cafe_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class TimeSlotUpdate(BaseProjectCreate):
    """Схема для обновления существующего временного слота."""

    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_active: Optional[bool] = None

    @model_validator(mode='after')
    def check_time_order(self) -> 'TimeSlotUpdate':
        """Проверяет, что `end_time` позже `start_time`, если оба заданы."""
        if self.start_time is not None and self.end_time is not None and self.end_time <= self.start_time:
            raise ValueError('end_time должно быть позже start_time.')
        return self
