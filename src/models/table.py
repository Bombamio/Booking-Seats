import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import CheckConstraint

from src.core.base_model import Base
from src.core.constants import DESCRIPTION_LENGTH, MIN_SEATS

if TYPE_CHECKING:
    from src.models.booking import BookingItem  # type: ignore # noqa: F401
    from src.models.cafe import Cafe  # type: ignore # noqa: F401


class Table(Base):
    """Модель для информации о столах для бронирования."""

    __table_args__ = (
        CheckConstraint(
            f'seat_number >= {MIN_SEATS}',
            name='check_seat_number',
        ),
    )
    cafe_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('cafes.id'),
        ondelete='CASCADE',
        index=True,
    )
    seat_number: Mapped[int]
    description: Mapped[str | None] = mapped_column(String(DESCRIPTION_LENGTH))

    cafe: Mapped['Cafe'] = relationship(back_populates='tables')
    booking_items: Mapped[list['BookingItem']] = relationship(
        back_populates='table',
    )

    def __repr__(self) -> str:
        """Вернет краткое понятное описание объекта модели."""
        return f'Table (id={self.id!r}, cafe={self.cafe_id!r})'
