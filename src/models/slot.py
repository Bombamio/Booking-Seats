import uuid
from datetime import time
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import CheckConstraint

from src.core.base_model import Base

if TYPE_CHECKING:
    from src.models import BookingItem, Cafe


class Slot(Base):
    """Модель Slot. Информация о временных слотах для бронирования в кафе."""

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

    cafe: Mapped['Cafe'] = relationship(back_populates='slots')
    booking_items: Mapped[list['BookingItem']] = relationship(
        back_populates='slot',
    )

    def __repr__(self) -> str:
        """Вернет краткое понятное описание объекта модели."""
        return f'Slot (id={self.id!r}, cafe={self.cafe_id!r})'
