import uuid

from sqlalchemy import String, ForeignKey, Integer, UUID
from sqlalchemy.orm import Mapped, mapped_column

from core import constants as ct
from core.base_model import Base


class Dishes(Base):
    """
    Модель Dishes. Информация о блюдах в меню.

    Поля:
    * `id` - uuid4, primary_key;
    * `name` - str, unique;
    * `description` - str;
    * `cafe_id` - int, ForeignKey;
    * `photo_id` - uuid4, ForeignKey;
    * `price` - int,
    * `created_at` - datetime,
    * `updated_at` - datetime,
    * `active` - boolean.
    """

    name: Mapped[str] = mapped_column(
        String(ct.MAX_NAME_LEN),
        unique=True
    )
    description: Mapped[str] = mapped_column(
        String(ct.MAX_DESCRIPTION_LEN),
        nullable=True
    )
    cafe_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey('cafe.id', name='fk_dishes_cafe_id_cafe')
    )
    photo_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey('photo.id', name='fk_dishes_photo_id_photo'),
        nullable=True
    )
    price: Mapped[int] = mapped_column(
        Integer
    )
