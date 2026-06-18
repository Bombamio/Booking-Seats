from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import CheckConstraint

from src.core.base_model import Base
from src.core.constants import MIN_SEATS


class Table(Base):
    """Модель для информации о столах для бронирования."""

    __table_args__ = (CheckConstraint(
        f'seat_number >= {MIN_SEATS}',
        name='check_seat_number'),
    )
    cafe_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('cafes.id'),
        nullable=False,
        index=True,
    )
    seat_number: Mapped[int] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(String(255))

    cafe: Mapped['Cafe'] = relationship(back_populates='tables')
    bookings: Mapped[list['Booking']] = relationship(back_populates='table')

    def __repr__(self) -> str:
        """Вернет краткое понятное описание объекта модели."""
        return f'Table (id={self.id!r}, cafe={self.cafe_id!r})'
