import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core import constants as ct
from src.core.base_model import Base
from src.models.association_tables import cafe_dishes

if TYPE_CHECKING:
    from src.models import Booking, BookingDish, Cafe


class Dish(Base):
    """Модель Dish. Информация о блюдах в меню.

    Поля:
    * `id` - uuid4, primary_key;
    * `name` - str, unique;
    * `description` - str;
    * `cafes` - list[Cafe], many-to-many;
    * `photo_id` - uuid4;
    * `price` - int;
    * `created_at` - datetime;
    * `updated_at` - datetime;
    * `is_active` - boolean.
    """

    __tablename__ = 'dishes'

    name: Mapped[str] = mapped_column(
        String(ct.MAX_NAME_LEN),
        unique=True,
    )
    description: Mapped[Optional[str]] = mapped_column(
        String(ct.MAX_DESCRIPTION_LEN),
    )
    photo_id: Mapped[Optional[uuid.UUID]]
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
