"""Импорты."""
import uuid

from datetime import date
from typing import Optional

from sqlalchemy import ForeignKey, String, Date, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core import constants as ct
from src.core.base_model import Base


class BookingStatus(str):
    """Статусы бронирования."""

    PENDING = 'PENDING'      # Ожидает подтверждения
    CONFIRMED = 'CONFIRMED'  # Подтверждено
    CANCELLED = 'CANCELLED'  # Отменено
    COMPLETED = 'COMPLETED'  # Завершено


class Booking(Base):
    """Модель Booking. Информация о бронировании.

    Поля:
    * `id` - uuid4, primary_key;
    * `user_id` - uuid4, ForeignKey (пользователь, который бронирует);
    * `cafe_id` - uuid4, ForeignKey (кафе, где бронируют);
    * `table_id` - uuid4, ForeignKey (стол, который бронируют);
    * `slot_id` - uuid4, ForeignKey (временной слот);
    * `booking_date` - date (дата бронирования);
    * `status` - str (статус бронирования);
    * `note` - str (примечание);
    * `created_at` - datetime;
    * `updated_at` - datetime;
    * `is_active` - boolean.
    """

    __tablename__ = 'bookings'

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'),
        index=True,
    )
    cafe_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('cafes.id', ondelete='CASCADE'),
        index=True,
    )
    table_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('tables.id', ondelete='CASCADE'),
        index=True,
    )
    slot_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('slots.id', ondelete='CASCADE'),
        index=True,
    )
    booking_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        Enum(BookingStatus),
        default=BookingStatus.PENDING,
        nullable=False,
    )
    note: Mapped[Optional[str]] = mapped_column(
        String(ct.MAX_DESCRIPTION_LEN),
        nullable=True,
    )

    # Связи с другими моделями
    user: Mapped['User'] = relationship(
        back_populates='bookings',
    )
    cafe: Mapped['Cafe'] = relationship()
    table: Mapped['Table'] = relationship(
        back_populates='booking_items',
    )
    slot: Mapped['Slot'] = relationship(
        back_populates='bookings',
    )

    def __repr__(self) -> str:
        """Возвращает однозначное строковое представление бронирования."""
        return (
            f'Booking(id={self.id!r}, user={self.user_id!r}, '
            f'date={self.booking_date!r})'
        )
