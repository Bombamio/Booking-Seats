import enum
import uuid
from datetime import date
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.models import BookingItem, Cafe, Dish, User

from sqlalchemy import Date, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core import constants as ct
from src.core.base_model import Base


class BookingStatus(enum.Enum):
    """Статусы бронирования."""

    PENDING = 'PENDING'  # Ожидает подтверждения
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
    * `dish_id` - uuid4, ForeignKey (блюда, который бронируют);
    * `slot_id` - uuid4, ForeignKey (временной слот);
    * `booking_date` - date (дата бронирования);
    * `status` - str (статус бронирования);
    * `note` - str (примечание);
    * `created_at` - datetime;
    * `updated_at` - datetime;
    * `is_active` - boolean.
    """

    # __tablename__ автоматом выставляется от названия класса, это
    # настройка из Base.

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'),
        index=True,
    )
    cafe_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('cafes.id', ondelete='CASCADE'),
        index=True,
    )
    booking_date: Mapped[date] = mapped_column(
        Date,
    )
    status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus),
        default=BookingStatus.PENDING,
    )
    note: Mapped[Optional[str]] = mapped_column(
        String(ct.MAX_DESCRIPTION_LEN),
    )

    # Связи с другими моделями.
    user: Mapped['User'] = relationship(
        back_populates='bookings',
    )
    cafe: Mapped['Cafe'] = relationship()
    dish: Mapped['Dish'] = relationship()
    booking_items: Mapped[list['BookingItem']] = relationship(
        back_populates='booking',
        cascade='all, delete-orphan',
        lazy='selectin',
    )

    def __repr__(self) -> str:
        """Возвращает однозначное строковое представление бронирования."""
        return f'Booking(id={self.id!r}, user={self.user_id!r}, date={self.booking_date!r})'
