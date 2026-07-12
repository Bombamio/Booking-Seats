"""ORM-модель кафе.

Описывает таблицу `cafes` и связи кафе с менеджерами, столами, слотами,
блюдами, акциями и бронированиями.

Классы:
   - `Cafe` — кафе в системе бронирования.

Связи:
   - `Cafe.managers` — менеджеры кафе.
   - `Cafe.tables` — столы кафе.
   - `Cafe.slots` — временные слоты кафе.
   - `Cafe.dishes` — блюда, доступные в кафе.
   - `Cafe.actions` — акции кафе.
   - `Cafe.bookings` — бронирования кафе.
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core import constants as ct
from src.core.base_model import Base
from src.models.association_tables import cafe_actions, cafe_dishes

if TYPE_CHECKING:
    from src.models import Action, Booking, Dish, Slot, Table, User


class Cafe(Base):
    """ORM-модель кафе."""

    name: Mapped[str] = mapped_column(
        String(ct.MAX_NAME_LEN),
    )
    address: Mapped[str] = mapped_column(
        String(ct.MAX_ADDRESS_LEN),
    )
    phone: Mapped[str] = mapped_column(
        String(ct.MAX_PHONE_LEN),
    )
    description: Mapped[str | None] = mapped_column(
        String(ct.MAX_DESCRIPTION_LEN),
    )
    photo_id: Mapped[uuid.UUID | None]

    managers: Mapped[list['User']] = relationship(
        back_populates='cafe',
    )

    tables: Mapped[list['Table']] = relationship(
        back_populates='cafe',
    )

    slots: Mapped[list['Slot']] = relationship(
        back_populates='cafe',
    )

    dishes: Mapped[list['Dish']] = relationship(
        secondary=cafe_dishes,
        back_populates='cafes',
    )

    actions: Mapped[list['Action']] = relationship(
        secondary=cafe_actions,
        back_populates='cafes',
    )

    bookings: Mapped[list['Booking']] = relationship(
        back_populates='cafe',
    )

    __table_args__ = (UniqueConstraint('name', 'address', name='uq_cafe_name_address'),)

    def __repr__(self) -> str:
        """Вернёт краткое строковое представление кафе."""
        return f'Cafe(id={self.id!r}, name={self.name!r})'
