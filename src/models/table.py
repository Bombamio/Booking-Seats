import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import CheckConstraint

from src.core import constants as ct
from src.core.base_model import Base

if TYPE_CHECKING:
    from src.models import Booking, Cafe


class Table(Base):
    """Модель Table. Информация о столах для бронирования."""

    __table_args__ = (
        CheckConstraint(
            f'seat_number >= {ct.MIN_SEATS}',
            name='check_seat_number',
        ),
    )
    cafe_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('cafes.id'),
        ondelete='CASCADE',
        index=True,
    )
    seat_number: Mapped[int]
    description: Mapped[Optional[str]] = mapped_column(
        String(ct.MAX_DESCRIPTION_LEN),
    )

    cafe: Mapped['Cafe'] = relationship(back_populates='tables')
    booking_items: Mapped[list['Booking']] = relationship(
        back_populates='table',
    )

    def __repr__(self) -> str:
        """Вернет краткое понятное описание объекта модели."""
        return f'Table (id={self.id!r}, cafe={self.cafe_id!r})'
