from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.action import Action
    from src.models.dish import Dish
    from src.models.slot import Slot
    from src.models.table import Table
    from src.models.user import User

import uuid

from sqlalchemy import UUID, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.base_model import Base
from src.models.association_tables import cafe_actions, cafe_dishes


class Cafe(Base):
    """Модель Cafe. Информация о кафе.

    Поля:
    * `id` - uuid4, primary_key;
    * `created_at` - datetime,
    * `updated_at` - datetime,
    * `is_active` - boolean,

    * `name` - str;
    * `address` - str;
    * `photo` - uuid4;
    * `description` - str;
    * `managers_id` - uuid4, ForeignKey;
    """

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    photo_id: Mapped[uuid.UUID | None] = mapped_column(UUID, nullable=True)

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
