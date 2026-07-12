"""ORM-модель позиции предзаказа блюда.

Описывает таблицу `booking_dishes` — связь бронирования и блюда с количеством.

Классы:
   - `BookingDish` — предзаказанное блюдо в бронировании.

Связи:
   - `BookingDish.dish` — блюдо в предзаказе.
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core import constants as ct
from src.core.base_model import Base

if TYPE_CHECKING:
    from src.models import Dish


class BookingDish(Base):
    """ORM-модель позиции предзаказа блюда в бронировании."""

    __tablename__ = 'booking_dishes'
    id = None
    is_active = None
    created_at = None
    updated_at = None

    __table_args__ = (
        CheckConstraint(
            f'quantity >= {ct.MIN_DISH_QUANTITY}',
            name='check_booking_dish_quantity',
        ),
    )

    booking_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('bookings.id', ondelete='RESTRICT'),
        primary_key=True,
    )
    dish_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('dishes.id', ondelete='RESTRICT'),
        primary_key=True,
    )
    quantity: Mapped[int] = mapped_column(default=ct.MIN_DISH_QUANTITY)

    dish: Mapped['Dish'] = relationship(
        back_populates='booking_dishes',
        lazy='selectin',
    )

    def __repr__(self) -> str:
        """Вернёт краткое строковое представление позиции предзаказа."""
        return (
            f'BookingDish(booking_id={self.booking_id!r}, '
            f'dish_id={self.dish_id!r}, quantity={self.quantity!r})'
        )
