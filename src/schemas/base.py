"""Базовые схемы для всех сущностей проекта.

Архитектура наследования разделена на входные и выходные ветки:

1. **Входные схемы** (Create, Update)
   - `BaseCreate` / `BaseUpdate` — базовые схемы без поля `description`.
   - `BaseDescriptionCreate` / `BaseDescriptionUpdate` — наследники с миксином `DescriptionMixin`.
   - `model_config.extra = 'forbid'` и валидация пустых строк — в `BaseCreate`.
   - В `BaseUpdate` — механизм `_not_null_fields`: запрещает передавать явный `null`
     для полей, которые в БД являются NOT NULL. Имена полей перечисляются
     в атрибуте `_not_null_fields: ClassVar[set[str]]` класса-наследника.
   - Поле `is_active` со значением по умолчанию `None` добавляется через `IsActiveMixin`
     в `BaseUpdate` и выходных схемах.

2. **Выходные схемы** (Info, ShortInfo)
   - `BaseShortInfo` / `BaseInfo` — базовые схемы без поля `description`.
   - `BaseDescriptionShortInfo` / `BaseDescriptionInfo` — наследники с `DescriptionMixin`.
   - `model_config.from_attributes = True` — в `FromAttributesMixin`, примешивается
     к выходным схемам.
   - Не содержат валидаторов входящих запросов.

Вспомогательные миксины:
   - `DescriptionMixin` — поле `description`, примешивается через `BaseDescription*`.
   - `FromAttributesMixin` — чтение из ORM-моделей, для выходных схем.
   - `IsActiveMixin` — флаг активности, используется в `BaseUpdate` и выходных схемах.
   - `PhotoIdMixin` — идентификатор фото, примешивается в схемы сущностей по необходимости.

Как создавать схемы для новой сущности:
   1. Создать миксин `EntityMixin` с полями сущности (поля — опциональны).
   2. Создать `EntityCreate(EntityMixin, BaseCreate)` или `EntityCreate(EntityMixin, BaseDescriptionCreate)`,
      если нужно поле `description`; переопределить обязательные поля.
   3. Создать `EntityUpdate(EntityMixin, BaseUpdate)` или `EntityUpdate(EntityMixin, BaseDescriptionUpdate)`.
   4. Создать `EntityInfo(EntityMixin, BaseInfo)` / `EntityShortInfo(EntityMixin, BaseShortInfo)`
      или их `BaseDescription*` варианты.
   5. При необходимости добавить другие миксины (например, `PhotoIdMixin`).

Важно:
   - Не добавлять валидаторы входящих запросов в выходные схемы.
   - Не допускать `null` в `_not_null_fields` для обязательных полей.
   - Для некоторых сущностей (например, User) эта схема наследования не подходит —
     схемы наследуют от `BaseModel` или выборочно от базовых классов.

Пример:
   - `src/schemas/booking.py`
   - `src/schemas/table.py`
"""

import uuid
from datetime import datetime
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.core import constants as ct


class DescriptionMixin:
    """Миксин с полем description."""

    description: str | None = Field(None, max_length=ct.MAX_DESCRIPTION_LEN)


class FromAttributesMixin:
    """Миксин для чтения схем из ORM-моделей."""

    model_config = ConfigDict(from_attributes=True)


class IsActiveMixin:
    """Добавляет признак активности (доступности) объекта в схему."""

    is_active: bool | None = Field(None, description='Признак активности (доступности) объекта')


class PhotoIdMixin:
    """Миксин для добавления photo_id в схему."""

    photo_id: uuid.UUID | None = None


class BaseCreate(BaseModel):
    """Базовая схема для создания объекта."""

    __abstract__ = True

    model_config = ConfigDict(extra='forbid')

    @model_validator(mode='before')
    @classmethod
    def reject_empty_strings(cls, values: Any) -> Any:
        """Проверит, что значения не являются пустыми строками."""
        if not isinstance(values, dict):
            return values
        for field_name in cls.model_fields:
            if field_name in values and isinstance(values[field_name], str) and values[field_name] == '':
                raise ValueError(f'Поле "{field_name}" не может быть пустой строкой.')
        return values


class BaseDescriptionCreate(DescriptionMixin, BaseCreate):
    """Базовая схема для создания объекта с полем description."""

    __abstract__ = True


class BaseUpdate(IsActiveMixin, BaseCreate):
    """Базовая схема для обновления объекта."""

    __abstract__ = True

    _not_null_fields: ClassVar[set[str]] = set()

    @model_validator(mode='before')
    @classmethod
    def reject_null_for_not_null_fields(cls, values: Any) -> Any:
        """Проверит, что значения не являются null для полей, которые заявлены в модели как обязательные."""
        if not isinstance(values, dict):
            return values
        not_null_fields = cls.__dict__.get('_not_null_fields', BaseUpdate._not_null_fields)
        for field_name in not_null_fields:
            if field_name in values and values[field_name] is None:
                raise ValueError(f'Поле "{field_name}" не может быть null.')
        return values


class BaseDescriptionUpdate(DescriptionMixin, BaseUpdate):
    """Базовая схема для обновления объекта с полем description."""

    __abstract__ = True


class BaseShortInfo(IsActiveMixin, FromAttributesMixin, BaseModel):
    """Базовая схема с краткой информацией об объекте."""

    __abstract__ = True

    id: uuid.UUID


class BaseDescriptionShortInfo(DescriptionMixin, BaseShortInfo):
    """Базовая схема с краткой информацией об объекте и полем description."""

    __abstract__ = True


class BaseInfo(BaseShortInfo):
    """Базовая абстрактная схема с полной информацией о объекте."""

    __abstract__ = True

    created_at: datetime
    updated_at: datetime


class BaseDescriptionInfo(DescriptionMixin, BaseInfo):
    """Базовая схема с полной информацией об объекте и полем description."""

    __abstract__ = True
