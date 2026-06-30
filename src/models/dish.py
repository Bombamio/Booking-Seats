import uuid
from typing import Optional

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core import constants as ct
from src.core.base_model import Base
from src.models import Cafe
from src.models.association_tables import cafe_dishes


class Dish(Base):
    """Модель Dish. Информация о блюдах в меню.

    Поля:
    * `id` - uuid4, primary_key;
    * `name` - str, unique;
    * `description` - str;
    * `cafes` - list[Cafe], many-to-many;
    * `photo` - uuid4, ForeignKey;
    * `price` - int;
    * `created_at` - datetime;
    * `updated_at` - datetime;
    * `is_active` - boolean.
    """

    name: Mapped[str] = mapped_column(
        String(ct.MAX_NAME_LEN),
        unique=True,
    )
    description: Mapped[Optional[str]] = mapped_column(
        String(ct.MAX_DESCRIPTION_LEN),
    )
    photo: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey('media.id'),
    )
    price: Mapped[int] = mapped_column(
        Integer,
    )

    cafes: Mapped[list['Cafe']] = relationship(
        secondary=cafe_dishes,
        back_populates='dishes',
    )
