import uuid
from typing import Optional

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core import constants as ct
from src.core.base_model import Base


class Dish(Base):
    """Модель Dish. Информация о блюдах в меню.

    Поля:
    * `id` - uuid4, primary_key;
    * `name` - str, unique;
    * `description` - str;
    * `cafes_id` - int, ForeignKey;
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
    # TODO: Заменить на many-to-many.
    cafes_id: Mapped[list[uuid.UUID]] = mapped_column(
        ForeignKey('cafe.id', name='fk_dish_cafe_id_cafe'),
    )
    photo: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey('media.id', name='fk_dish_photo_id_photo'),
    )
    price: Mapped[int] = mapped_column(
        Integer,
    )
