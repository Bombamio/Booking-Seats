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
   - `TimeSlotInfo` — полный ответ API с кафе и метаданными.

Наследование:
   - входные схемы — `BaseDescriptionCreate` / `BaseDescriptionUpdate`;
   - выходные схемы — `BaseDescriptionShortInfo` / `BaseDescriptionInfo`.

Общие правила наследования и базовые миксины — в `src/schemas/base.py`.
"""

from datetime import time
from typing import ClassVar, Self

from pydantic import model_validator

from src.schemas.base import (
    BaseDescriptionCreate,
    BaseDescriptionInfo,
    BaseDescriptionShortInfo,
    BaseDescriptionUpdate,
)
from src.schemas.cafe import CafeShortInfo


class TimeSlotBaseMixin:
    """Миксин с атрибутами временного слота."""

    start_time: time
    end_time: time


class TimeSlotValidationMixin:
    """Миксин с валидацией порядка времени слота."""

    @model_validator(mode='after')
    def check_time_order(self) -> Self:
        """Проверяет, что `end_time` позже `start_time`."""
        if self.end_time <= self.start_time:
            raise ValueError('end_time должно быть позже start_time.')
        return self


class TimeSlotCreate(TimeSlotValidationMixin, TimeSlotBaseMixin, BaseDescriptionCreate):
    """Схема для создания нового временного слота.

    Поля (включая унаследованные):
        description (str | None): описание слота; необязательное.
        start_time (time): время начала слота; обязательное.
        end_time (time): время окончания слота; обязательное.
    """


class TimeSlotUpdate(TimeSlotValidationMixin, BaseDescriptionUpdate):
    """Схема для обновления существующего временного слота.

    Поля (включая унаследованные):
        description (str | None): описание слота; необязательное.
        start_time (time | None): время начала слота; необязательное; явный null запрещён.
        end_time (time | None): время окончания слота; необязательное; явный null запрещён.
        is_active (bool | None): признак активности; необязательное; явный null запрещён.
    """

    start_time: time | None = None
    end_time: time | None = None

    _not_null_fields: ClassVar[set[str]] = {'start_time', 'end_time', 'is_active'}

    @model_validator(mode='after')
    def check_time_order(self) -> Self:
        """Проверяет порядок времени только если оба поля переданы."""
        if self.start_time is None or self.end_time is None:
            return self
        if self.end_time <= self.start_time:
            raise ValueError('end_time должно быть позже start_time.')
        return self


class TimeSlotShortInfo(TimeSlotBaseMixin, BaseDescriptionShortInfo):
    """Краткая информация о временном слоте.

    Поля (включая унаследованные):
        description (str | None): описание слота.
        is_active (bool | None): признак активности.
        id (UUID): идентификатор слота.
        start_time (time): время начала слота.
        end_time (time): время окончания слота.
    """


class TimeSlotInfo(TimeSlotBaseMixin, BaseDescriptionInfo):
    """Полная информация о временном слоте.

    Поля (включая унаследованные):
        description (str | None): описание слота.
        is_active (bool | None): признак активности.
        id (UUID): идентификатор слота.
        created_at (datetime): дата создания.
        updated_at (datetime): дата обновления.
        start_time (time): время начала слота.
        end_time (time): время окончания слота.
        cafe (CafeShortInfo): кафе слота.
    """

    cafe: CafeShortInfo
