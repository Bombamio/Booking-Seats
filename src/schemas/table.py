"""Схемы столика.

Модуль описывает входные и выходные схемы для управления столиками в кафе.

Локальные миксины:
   - `TableBaseMixin` — количество мест за столиком.

Схемы API:
   - `TableCreate` — создание столика; `description` опционально.
   - `TableUpdate` — частичное обновление; `seat_number` и `is_active` не принимают `null`.
   - `TableShortInfo` — краткая информация для вложенных ответов.
   - `TableInfo` — полный ответ API с данными кафе.

Наследование:
   - входные схемы — `BaseDescriptionCreate` / `BaseDescriptionUpdate`;
   - выходные схемы — `BaseDescriptionShortInfo` / `BaseDescriptionInfo`.

Общие правила наследования и базовые миксины — в `src/schemas/base.py`.
"""

from typing import ClassVar

from pydantic import Field, PositiveInt

from src.core.constants import MIN_SEATS
from src.schemas.base import (
    BaseDescriptionCreate,
    BaseDescriptionInfo,
    BaseDescriptionShortInfo,
    BaseDescriptionUpdate,
)
from src.schemas.cafe import CafeShortInfo


class TableBaseMixin:
    """Миксин с атрибутами столика."""

    seat_number: PositiveInt = Field(description=f'Количество мест столика (не менее {MIN_SEATS}).')


class TableCreate(TableBaseMixin, BaseDescriptionCreate):
    """Схема данных для создания столика в кафе.

    Поля (включая унаследованные):
        description (str | None): описание столика; необязательное.
        seat_number (PositiveInt): количество мест; обязательное.
    """


class TableUpdate(BaseDescriptionUpdate):
    """Схема данных для обновления столика в кафе.

    Поля (включая унаследованные):
        description (str | None): описание столика; необязательное.
        seat_number (PositiveInt | None): количество мест; необязательное; явный null запрещён.
        is_active (bool | None): признак активности; необязательное; явный null запрещён.
    """

    seat_number: PositiveInt | None = Field(
        None,
        description='Количество мест столика (не менее {MIN_SEATS}).',
    )
    _not_null_fields: ClassVar[set[str]] = {'seat_number', 'is_active'}


class TableShortInfo(TableBaseMixin, BaseDescriptionShortInfo):
    """Схема данных для предоставления краткого инфо о столике.

    Поля (включая унаследованные):
        description (str | None): описание столика.
        is_active (bool | None): признак активности.
        id (UUID): идентификатор столика.
        seat_number (PositiveInt): количество мест.
    """


class TableInfo(TableBaseMixin, BaseDescriptionInfo):
    """Схема данных для предоставления информации о столике.

    Поля (включая унаследованные):
        description (str | None): описание столика.
        is_active (bool | None): признак активности.
        id (UUID): идентификатор столика.
        created_at (datetime): дата создания.
        updated_at (datetime): дата обновления.
        seat_number (PositiveInt): количество мест.
        cafe (CafeShortInfo): кафе столика.
    """

    cafe: CafeShortInfo
