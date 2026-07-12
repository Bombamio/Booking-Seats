"""ORM-модель стола.

Описывает таблицу `tables` и связи стола с кафе и бронированиями.

Классы:
   - `Table` — стол для бронирования в кафе.

Связи:
   - `Table.cafe` — кафе, в котором расположен стол.
   - `Table.booking_items` — позиции бронирования с этим столом.
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import CheckConstraint

from src.core import constants as ct
from src.core.base_model import Base

if TYPE_CHECKING:
    from src.models import BookingItem, Cafe


class Table(Base):
    """ORM-модель стола для бронирования."""

    __table_args__ = (
        CheckConstraint(
            f'seat_number >= {ct.MIN_SEATS}',
            name='check_seat_number',
        ),
    )
    cafe_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('cafes.id', ondelete='RESTRICT'),
        index=True,
    )
    seat_number: Mapped[int]
    description: Mapped[str | None] = mapped_column(
        String(ct.MAX_DESCRIPTION_LEN),
    )

    cafe: Mapped['Cafe'] = relationship(back_populates='tables')
    booking_items: Mapped[list['BookingItem']] = relationship(
        back_populates='table',
    )

    def __repr__(self) -> str:
        """Вернёт краткое строковое представление стола."""
        return f'Table(id={self.id!r}, cafe_id={self.cafe_id!r}, seat_number={self.seat_number!r})'
