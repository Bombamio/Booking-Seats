"""Схемы временного слота.

Модуль описывает входные и выходные схемы для управления слотами бронирования в кафе.

Локальные миксины:
   - `TimeSlotBaseMixin` — время начала и окончания слота.
   - `TimeSlotValidationMixin` — `end_time` должно быть позже `start_time`.

Схемы API:
   - `TimeSlotCreate` — создание слота; `description` опционально.
   - `TimeSlotUpdate` — частичное обновление; `start_time`, `end_time` и `is_active`
     не принимают `null`.
   - `TimeSlotShortInfo` — краткая информация для вложенных ответов.
   - `TimeSlotInfo` — полный ответ API с `cafe_id` и метаданными.

Наследование:
   - входные схемы — `BaseDescriptionCreate` / `BaseDescriptionUpdate`;
   - выходные схемы — `BaseDescriptionShortInfo` / `BaseDescriptionInfo`.

Общие правила наследования и базовые миксины — в `src/schemas/base.py`.
"""

import uuid
from datetime import datetime

from pydantic import model_validator

from src.schemas.base import (
    BaseDescriptionCreate,
    BaseDescriptionInfo,
    BaseDescriptionShortInfo,
    BaseDescriptionUpdate,
)


class TimeSlotBaseMixin:
    """Миксин с атрибутами временного слота."""

    start_time: datetime
    end_time: datetime


class TimeSlotValidationMixin:
    """Миксин с валидацией порядка времени слота."""

    @model_validator(mode='after')
    def check_time_order(self) -> 'TimeSlotCreate':
        """Проверяет, что `end_time` позже `start_time`."""
        if self.end_time <= self.start_time:
            raise ValueError('end_time должно быть позже start_time.')
        return self


class TimeSlotCreate(TimeSlotValidationMixin, TimeSlotBaseMixin, BaseDescriptionCreate):
    """Схема для создания нового временного слота.

    Поля (включая унаследованные):
        description (str | None): описание слота; необязательное.
        start_time (datetime): время начала слота; обязательное.
        end_time (datetime): время окончания слота; обязательное.
    """


class TimeSlotUpdate(TimeSlotValidationMixin, TimeSlotBaseMixin, BaseDescriptionUpdate):
    """Схема для обновления существующего временного слота.

    Поля (включая унаследованные):
        description (str | None): описание слота; необязательное.
        start_time (datetime | None): время начала слота; необязательное; явный null запрещён.
        end_time (datetime | None): время окончания слота; необязательное; явный null запрещён.
        is_active (bool | None): признак активности; необязательное; явный null запрещён.
    """

    start_time: datetime | None = None
    end_time: datetime | None = None

    _not_null_fields: set[str] = {'start_time', 'end_time', 'is_active'}


class TimeSlotShortInfo(TimeSlotBaseMixin, BaseDescriptionShortInfo):
    """Краткая информация о временном слоте.

    Поля (включая унаследованные):
        description (str | None): описание слота.
        is_active (bool | None): признак активности.
        id (UUID): идентификатор слота.
        start_time (datetime): время начала слота.
        end_time (datetime): время окончания слота.
    """


class TimeSlotInfo(TimeSlotBaseMixin, BaseDescriptionInfo):
    """Полная информация о временном слоте.

    Поля (включая унаследованные):
        description (str | None): описание слота.
        is_active (bool | None): признак активности.
        id (UUID): идентификатор слота.
        created_at (datetime): дата создания.
        updated_at (datetime): дата обновления.
        start_time (datetime): время начала слота.
        end_time (datetime): время окончания слота.
        cafe_id (UUID): идентификатор кафе.
    """

    cafe_id: uuid.UUID
