"""CRUD-слой бронирований.

Модуль описывает операции чтения и записи для модели `Booking`.

Классы:
   - `CRUDBooking` — выборка с деталями, проверка конфликтов стол-слот,
     замена позиций бронирования.

Связанные слои:
   - бизнес-логика — в `src/services/booking.py`.
"""

import uuid
from datetime import date
from typing import Any, Sequence

from sqlalchemy import delete, exists, select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.crud.base import CRUDBase
from src.models import Booking, BookingDish, BookingItem, BookingStatus, Cafe, Dish


class CRUDBooking(CRUDBase):
    """CRUD функции для модели Booking."""

    @staticmethod
    def _details_options() -> tuple:
        """Вернет опции загрузки связей для ответа API."""
        return (
            selectinload(Booking.user),
            selectinload(Booking.cafe).selectinload(Cafe.managers),
            selectinload(Booking.booking_items).selectinload(BookingItem.table),
            selectinload(Booking.booking_items).selectinload(BookingItem.slot),
            selectinload(Booking.booking_dishes).selectinload(BookingDish.dish).selectinload(Dish.cafes),
        )

    async def get_with_details(
        self,
        session: AsyncSession,
        *filters: Any,
    ) -> Booking | None:
        """Вернет бронирование со связями для ответа API."""
        result = await session.execute(
            select(self.model).options(*self._details_options()).where(*filters),
        )
        return result.scalars().first()

    async def get_multi_with_details(
        self,
        session: AsyncSession,
        *filters: Any,
    ) -> Sequence[Booking]:
        """Вернет список бронирований со связями для ответа API."""
        result = await session.execute(
            select(self.model)
            .options(*self._details_options())
            .where(*filters)
            .order_by(
                self.model.booking_date.desc(),
                self.model.created_at.desc(),
            ),
        )
        return result.scalars().all()

    async def has_table_slot_conflicts(
        self,
        tables_slots: list[tuple[uuid.UUID, uuid.UUID]],
        booking_date: date,
        session: AsyncSession,
        exclude_booking_id: uuid.UUID | None = None,
    ) -> bool:
        """Проверит, есть ли активные брони на переданные пары стол-слот."""
        filters = [
            self.model.booking_date == booking_date,
            self.model.is_active.is_(True),
            self.model.status.in_(
                (
                    BookingStatus.BOOKING,
                    BookingStatus.ACTIVE,
                ),
            ),
            self.model.booking_items.any(
                tuple_(BookingItem.table_id, BookingItem.slot_id).in_(
                    tables_slots,
                ),
            ),
        ]
        if exclude_booking_id:
            filters.append(self.model.id != exclude_booking_id)

        query = select(exists().where(*filters))
        return bool(await session.scalar(query))

    async def replace_booking_items(
        self,
        booking: Booking,
        tables_slots: list[tuple[uuid.UUID, uuid.UUID]],
        session: AsyncSession,
    ) -> None:
        """Заменит пары стол-слот у бронирования."""
        await session.execute(
            delete(BookingItem).where(BookingItem.booking_id == booking.id),
        )
        session.add_all(
            BookingItem(
                booking_id=booking.id,
                table_id=table_id,
                slot_id=slot_id,
            )
            for table_id, slot_id in tables_slots
        )


booking_crud = CRUDBooking(Booking)
