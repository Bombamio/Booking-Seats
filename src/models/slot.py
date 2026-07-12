"""ORM-модель временного слота.

Описывает таблицу `slots` и связи слота с кафе и позициями бронирования.

Классы:
   - `Slot` — временной интервал бронирования в кафе.

Связи:
   - `Slot.cafe` — кафе, к которому относится слот.
   - `Slot.booking_items` — пары стол-слот в бронированиях.
"""

import uuid
from datetime import time
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import CheckConstraint

from src.core import constants as ct
from src.core.base_model import Base

if TYPE_CHECKING:
    from src.models import BookingItem, Cafe


class Slot(Base):
    """ORM-модель временного слота бронирования."""

    __table_args__ = (
        CheckConstraint(
            'end_time > start_time',
            name='check_slot_time_order',
        ),
    )

    cafe_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('cafes.id', ondelete='RESTRICT'),
        index=True,
    )
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    description: Mapped[str | None] = mapped_column(
        String(ct.MAX_DESCRIPTION_LEN),
    )

    cafe: Mapped['Cafe'] = relationship(back_populates='slots')
    booking_items: Mapped[list['BookingItem']] = relationship(
        back_populates='slot',
    )

    def __repr__(self) -> str:
        """Вернёт краткое строковое представление временного слота."""
        return (
            f'Slot(id={self.id!r}, cafe_id={self.cafe_id!r}, '
            f'start_time={self.start_time!r}, end_time={self.end_time!r})'
        )
