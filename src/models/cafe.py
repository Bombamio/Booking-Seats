from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.models import Action, Dish, Slot, Table, User

import uuid

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core import constants as ct
from src.core.base_model import Base
from src.models.association_tables import cafe_actions, cafe_dishes


class Cafe(Base):
    """Модель Cafe. Информация о кафе.

    Поля:
    * `id` - uuid4, primary_key;
    * `created_at` - datetime;
    * `updated_at` - datetime;
    * `is_active` - boolean;
    * `name` - str;
    * `address` - str;
    * `photo_id` - uuid4;
    * `description` - str;
    * `managers_id` - uuid4;
    """

    # TODO: двойная валидация полей name и address.
    name: Mapped[str] = mapped_column(
        String(ct.MAX_NAME_LEN),
    )
    address: Mapped[str] = mapped_column(
        String(ct.MAX_ADDRESS_LEN),
    )
    phone: Mapped[str] = mapped_column(
        String(ct.MAX_PHONE_LEN),
    )
    description: Mapped[Optional[str]] = mapped_column(
        String(ct.MAX_DESCRIPTION_LEN),
    )
    photo_id: Mapped[Optional[uuid.UUID]]

    managers: Mapped[list[User]] = relationship(
        back_populates='cafe',
    )

    tables: Mapped[list[Table]] = relationship(
        back_populates='cafe',
    )

    slots: Mapped[list[Slot]] = relationship(
        back_populates='cafe',
    )

    dishes: Mapped[list[Dish]] = relationship(
        secondary=cafe_dishes,
        back_populates='cafes',
    )

    actions: Mapped[list[Action]] = relationship(
        secondary=cafe_actions,
        back_populates='cafes',
    )

    __table_args__ = (UniqueConstraint('name', 'address', name='uq_cafe_name_address'),)
