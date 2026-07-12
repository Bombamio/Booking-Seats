"""ORM-модель блюда.

Описывает таблицу `dishes` и связи блюда с кафе и бронированиями.

Классы:
   - `Dish` — блюдо в меню.

Связи:
   - `Dish.cafes` — кафе, в которых доступно блюдо.
   - `Dish.bookings` — бронирования с предзаказом блюда.
   - `Dish.booking_dishes` — позиции предзаказа.
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core import constants as ct
from src.core.base_model import Base
from src.models.association_tables import cafe_dishes

if TYPE_CHECKING:
    from src.models import Booking, BookingDish, Cafe


class Dish(Base):
    """ORM-модель блюда."""

    __tablename__ = 'dishes'

    name: Mapped[str] = mapped_column(
        String(ct.MAX_NAME_LEN),
        unique=True,
    )
    description: Mapped[str | None] = mapped_column(
        String(ct.MAX_DESCRIPTION_LEN),
    )
    photo_id: Mapped[uuid.UUID | None]
    price: Mapped[int] = mapped_column(
        Integer,
    )

    cafes: Mapped[list['Cafe']] = relationship(
        secondary=cafe_dishes,
        back_populates='dishes',
        lazy='raise',
    )
    bookings: Mapped[list['Booking']] = relationship(
        secondary='booking_dishes',
        back_populates='dishes',
        viewonly=True,
    )
    booking_dishes: Mapped[list['BookingDish']] = relationship(
        back_populates='dish',
    )

    def __repr__(self) -> str:
        """Вернёт краткое строковое представление блюда."""
        return f'Dish(id={self.id!r}, name={self.name!r}, price={self.price!r})'
