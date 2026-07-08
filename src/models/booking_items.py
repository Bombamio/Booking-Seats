import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.base_model import Base

if TYPE_CHECKING:
    from src.models import Slot, Table


class BookingItem(Base):
    """Модель BookingItem. Связка пар стол-слот при бронировании."""

    __table_args__ = (
        UniqueConstraint(
            'booking_id',
            'table_id',
            'slot_id',
            name='uq_booking_item',
        ),
    )

    booking_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            'bookings.id',
            ondelete='RESTRICT',
        ),
    )
    table_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            'tables.id',
            ondelete='RESTRICT',
        ),
    )
    slot_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            'slots.id',
            ondelete='RESTRICT',
        ),
    )

    table: Mapped['Table'] = relationship(
        back_populates='booking_items',
        lazy='raise',
    )
    slot: Mapped['Slot'] = relationship(
        back_populates='booking_items',
        lazy='raise',
    )

    def __repr__(self) -> str:
        """Вернет краткое представление связки бронирования."""
        return (
            f'BookingItem(id={self.id!r}, '
            f'booking_id={self.booking_id!r}, '
            f'table_id={self.table_id!r}, '
            f'slot_id={self.slot_id!r})'
        )
