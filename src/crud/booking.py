import uuid
from datetime import date
from typing import Any, Optional, Sequence

from sqlalchemy import delete, exists, select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.crud.base import CRUDBase
from src.models import Booking, BookingDish, BookingItem, BookingStatus, Cafe, Dish, User, UserRole


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
    ) -> Optional[Booking]:
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

    async def get_by_user(
        self,
        user_id: uuid.UUID,
        session: AsyncSession,
        include_inactive: bool = False,
    ) -> Sequence[Booking]:
        """Получение всех бронирований пользователя."""
        filters = [self.model.user_id == user_id]

        if not include_inactive:
            filters.append(self.model.is_active.is_(True))

        result = await session.execute(
            select(self.model)
            .options(*self._details_options())
            .where(*filters)
            .order_by(
                self.model.booking_date.desc(),
            ),
        )
        return result.scalars().all()

    async def get_by_cafe(
        self,
        cafe_id: uuid.UUID,
        session: AsyncSession,
        booking_date: Optional[date] = None,
        include_inactive: bool = False,
    ) -> Sequence[Booking]:
        """Получение всех бронирований кафе (опционально по дате)."""
        filters = [self.model.cafe_id == cafe_id]

        if booking_date:
            filters.append(self.model.booking_date == booking_date)

        if not include_inactive:
            filters.append(self.model.is_active.is_(True))

        result = await session.execute(
            select(self.model)
            .options(*self._details_options())
            .where(*filters)
            .order_by(
                self.model.booking_date,
                self.model.created_at,
            ),
        )
        return result.scalars().all()

    async def get_by_table_slot_and_date(
        self,
        table_id: uuid.UUID,
        slot_id: uuid.UUID,
        booking_date: date,
        session: AsyncSession,
        exclude_booking_id: Optional[uuid.UUID] = None,
    ) -> Sequence[Booking]:
        """Получение бронирований конкретной пары стол-слот на дату."""
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
                (BookingItem.table_id == table_id) & (BookingItem.slot_id == slot_id),
            ),
        ]

        if exclude_booking_id:
            filters.append(self.model.id != exclude_booking_id)

        result = await session.execute(select(self.model).where(*filters))
        return result.scalars().all()

    async def get_by_manager(
        self,
        user: User,
        session: AsyncSession,
        booking_date: Optional[date] = None,
        include_inactive: bool = False,
    ) -> Sequence[Booking]:
        """Получение бронирований для менеджера (только его кафе)."""
        if user.role != UserRole.MANAGER:
            return []

        filters = [self.model.cafe_id == user.cafe_id]

        if booking_date:
            filters.append(self.model.booking_date == booking_date)

        if not include_inactive:
            filters.append(self.model.is_active.is_(True))

        result = await session.execute(
            select(self.model)
            .options(*self._details_options())
            .where(*filters)
            .order_by(
                self.model.booking_date,
                self.model.created_at,
            ),
        )
        return result.scalars().all()

    async def has_table_slot_conflicts(
        self,
        tables_slots: list[tuple[uuid.UUID, uuid.UUID]],
        booking_date: date,
        session: AsyncSession,
        exclude_booking_id: Optional[uuid.UUID] = None,
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

    async def update_status(
        self,
        booking_id: uuid.UUID,
        status: BookingStatus,
        session: AsyncSession,
    ) -> Optional[Booking]:
        """Обновление статуса бронирования."""
        booking = await self.get(
            session,
            self.model.id == booking_id,
        )
        if not booking:
            return None

        booking.status = status
        session.add(booking)
        await session.commit()
        await session.refresh(booking)
        return booking


booking_crud = CRUDBooking(Booking)
