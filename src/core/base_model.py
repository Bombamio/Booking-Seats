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
    """Возвращает текущее дата/время UTC."""
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """Базовый класс для всех таблиц."""

    @declared_attr.directive
    def __tablename__(cls) -> str:  # noqa: N805
        """Возвращает имя таблицы на основе названия класса."""
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
    )
