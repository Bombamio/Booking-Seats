from typing import Any, Optional

from pydantic import Field, PositiveInt, model_validator

from src.core.constants import MIN_SEATS
from src.schemas.base import (
    BaseProjectCreate,
    BaseProjectInfo,
    BaseProjectShortInfo,
)


class TableBaseMixin:
    """Миксин с атрибутами столика."""

    seat_number: Optional[PositiveInt] = Field(
        None,
        examples=[MIN_SEATS],
        description=f'Количество мест столика (не менее {MIN_SEATS}).',
    )


class TableCreate(TableBaseMixin, BaseProjectCreate):
    """Схема данных для создания столика в кафе."""

    seat_number: PositiveInt = Field(
        examples=[MIN_SEATS],
        description=f'Количество мест столика (не менее {MIN_SEATS}).',
    )


class TableInfo(TableBaseMixin, BaseProjectInfo):
    """Схема данных для предоставления информации о столике."""

    cafe: Any  # до появления схемы CafeShortInfo


class TableShortInfo(TableBaseMixin, BaseProjectShortInfo):
    """Схема данных для предоставления краткого инфо о столике."""


class TableUpdate(TableBaseMixin, BaseProjectCreate):
    """Схема данных для создания столика в кафе."""

    is_active: Optional[bool] = Field(None)

    @model_validator(mode='before')
    @classmethod
    def reject_null(cls, values: Any) -> Any:
        """Сообщит об ошибке, если в полях запроса передано значение Null."""
        for field in cls.model_fields:
            if field in values and values[field] is None:
                raise ValueError(f'Поле "{field}" не может быть пустым.')
        return values
