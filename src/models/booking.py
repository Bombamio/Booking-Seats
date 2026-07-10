import enum
import uuid
from datetime import date
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.models import BookingDish, BookingItem, Cafe, Dish, User

from sqlalchemy import CheckConstraint, Date, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core import constants as ct
from src.core.base_model import Base


class BookingStatus(enum.Enum):
    """Статусы бронирования."""

    BOOKING = 'BOOKING'
    CANCELED = 'CANCELED'
    ACTIVE = 'ACTIVE'
    COMPLETED = 'COMPLETED'


class Booking(Base):
    """Модель Booking. Информация о бронировании."""

    __table_args__ = (CheckConstraint('booking_date >= current_date', name='check_booking_date'),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('users.id', ondelete='RESTRICT'),
        index=True,
    )
    cafe_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('cafes.id', ondelete='RESTRICT'),
        index=True,
    )
    booking_date: Mapped[date] = mapped_column(
        Date,
    )
    status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus),
        default=BookingStatus.BOOKING,
    )
    note: Mapped[Optional[str]] = mapped_column(
        String(ct.MAX_DESCRIPTION_LEN),
    )
    guest_number: Mapped[int] = mapped_column(default=ct.DEFAULT_GUEST_NUMBER)
    reminder_task_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        nullable=True,
    )

    user: Mapped['User'] = relationship(
        back_populates='bookings',
        lazy='selectin',
    )
    cafe: Mapped['Cafe'] = relationship(
        back_populates='bookings',
        lazy='selectin',
    )
    booking_items: Mapped[list['BookingItem']] = relationship(
        cascade='all, delete-orphan',
        lazy='raise',
    )
    booking_dishes: Mapped[list['BookingDish']] = relationship(
        cascade='all, delete-orphan',
        lazy='raise',
    )
    dishes: Mapped[list['Dish']] = relationship(
        secondary='booking_dishes',
        back_populates='bookings',
        viewonly=True,
        lazy='raise',
    )

    def __repr__(self) -> str:
        """Возвращает однозначное строковое представление бронирования."""
        return f'Booking(id={self.id!r}, user={self.user_id!r}, date={self.booking_date!r})'
