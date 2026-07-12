"""Базовая ORM-модель SQLAlchemy.

Модуль описывает общие поля и поведение всех таблиц проекта.

Классы:
   - `Base` — декларативная база с ``id``, ``is_active``, ``created_at``, ``updated_at``.
   - `LinkModelBase` — база для связующих таблиц без общих полей ``Base``.

Функции:
   - `get_utc_now` — текущее время UTC для полей модели.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import UUID, Boolean, DateTime, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
)


def get_utc_now() -> datetime:
    """Вернёт текущие дату и время в UTC."""
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """Базовый класс для всех ORM-таблиц."""

    @declared_attr.directive
    def __tablename__(cls) -> str:  # noqa: N805
        """Вернёт имя таблицы на основе названия класса."""
        return f'{cls.__name__.lower()}s'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
        default=uuid.uuid4,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default='true',
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=get_utc_now,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=get_utc_now,
        server_onupdate=func.now(),
    )


class LinkModelBase(DeclarativeBase):
    """Базовый класс для связующих таблиц без ``id``, ``is_active`` и timestamps."""

    metadata = Base.metadata
