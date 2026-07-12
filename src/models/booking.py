"""ORM-модели бронирования.

Описывает таблицу `bookings`, статусы бронирования и связи с пользователем,
кафе, столами, слотами и блюдами.

Классы:
   - `BookingStatus` — допустимые статусы бронирования.
   - `Booking` — бронирование столика в кафе.

Связи:
   - `Booking.user` — пользователь, создавший бронирование.
   - `Booking.cafe` — кафе бронирования.
   - `Booking.booking_items` — пары стол-слот.
   - `Booking.booking_dishes` — предзаказанные блюда.
"""

import uuid
from datetime import date
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core import constants as ct
from src.core.base_model import Base

if TYPE_CHECKING:
    from src.models import BookingDish, BookingItem, Cafe, Dish, User


class BookingStatus(StrEnum):
    """Статусы бронирования."""

    BOOKING = 'BOOKING'
    CANCELED = 'CANCELED'
    ACTIVE = 'ACTIVE'
    COMPLETED = 'COMPLETED'


class Booking(Base):
    """ORM-модель бронирования."""

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
    note: Mapped[str | None] = mapped_column(
        String(ct.MAX_DESCRIPTION_LEN),
    )
    guest_number: Mapped[int] = mapped_column(default=ct.DEFAULT_GUEST_NUMBER)
    reminder_task_id: Mapped[str | None] = mapped_column(
        String(ct.UUID_STRING_LEN),
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
        """Вернёт краткое строковое представление бронирования."""
        return f'Booking(id={self.id!r}, user_id={self.user_id!r}, date={self.booking_date!r})'
