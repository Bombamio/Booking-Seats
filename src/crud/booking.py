"""Импорты."""
import uuid

from datetime import date
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.models import Booking, User
from src.models.user import UserRole


class CRUDBooking(CRUDBase):
    """CRUD функции для модели Booking."""

    async def get_by_user(
        self,
        user_id: uuid.UUID,
        session: AsyncSession,
        include_inactive: bool = False,
    ) -> list[Booking]:
        """Получение всех бронирований пользователя."""
        filters = [self.model.user_id == user_id]

        if not include_inactive:
            filters.append(self.model.is_active.is_(True))

        result = await session.execute(
            select(self.model).where(*filters).order_by(
                self.model.booking_date.desc()
            )
        )
        return list(result.scalars().all())

    async def get_by_cafe(
        self,
        cafe_id: uuid.UUID,
        session: AsyncSession,
        booking_date: Optional[date] = None,
        include_inactive: bool = False,
    ) -> list[Booking]:
        """Получение всех бронирований кафе (опционально по дате)."""
        filters = [self.model.cafe_id == cafe_id]

        if booking_date:
            filters.append(self.model.booking_date == booking_date)

        if not include_inactive:
            filters.append(self.model.is_active.is_(True))

        result = await session.execute(
            select(self.model).where(*filters).order_by(
                self.model.booking_date,
                self.model.slot_id
            )
        )
        return list(result.scalars().all())

    async def get_by_table_and_date(
        self,
        table_id: uuid.UUID,
        booking_date: date,
        session: AsyncSession,
        exclude_booking_id: Optional[uuid.UUID] = None,
    ) -> list[Booking]:
        """Получение бронирований конкретного стола на дату."""
        filters = [
            self.model.table_id == table_id,
            self.model.booking_date == booking_date,
            self.model.is_active.is_(True),
            self.model.status.in_(['PENDING', 'CONFIRMED']),
        ]

        if exclude_booking_id:
            filters.append(self.model.id != exclude_booking_id)

        result = await session.execute(select(self.model).where(*filters))
        return list(result.scalars().all())

    async def get_by_slot_and_date(
        self,
        slot_id: uuid.UUID,
        booking_date: date,
        session: AsyncSession,
        exclude_booking_id: Optional[uuid.UUID] = None,
    ) -> list[Booking]:
        """Получение бронирований конкретного слота на дату."""
        filters = [
            self.model.slot_id == slot_id,
            self.model.booking_date == booking_date,
            self.model.is_active.is_(True),
            self.model.status.in_(['PENDING', 'CONFIRMED']),
        ]

        if exclude_booking_id:
            filters.append(self.model.id != exclude_booking_id)

        result = await session.execute(select(self.model).where(*filters))
        return list(result.scalars().all())

    async def get_by_manager(
        self,
        user: User,
        session: AsyncSession,
        booking_date: Optional[date] = None,
        include_inactive: bool = False,
    ) -> list[Booking]:
        """Получение бронирований для менеджера (только его кафе)."""
        if user.role != UserRole.MANAGER:
            return []

        filters = [self.model.cafe_id == user.cafe_id]

        if booking_date:
            filters.append(self.model.booking_date == booking_date)

        if not include_inactive:
            filters.append(self.model.is_active.is_(True))

        result = await session.execute(
            select(self.model).where(*filters).order_by(
                self.model.booking_date,
                self.model.slot_id
            )
        )
        return list(result.scalars().all())

    async def check_availability(
        self,
        table_id: uuid.UUID,
        slot_id: uuid.UUID,
        booking_date: date,
        session: AsyncSession,
        exclude_booking_id: Optional[uuid.UUID] = None,
    ) -> bool:
        """Проверка доступности стола и слота на конкретную дату."""
        table_bookings = await self.get_by_table_and_date(
            table_id, booking_date, session, exclude_booking_id
        )

        slot_bookings = await self.get_by_slot_and_date(
            slot_id, booking_date, session, exclude_booking_id
        )

        for booking in table_bookings:
            if booking.status == 'CONFIRMED':
                return False

        for booking in slot_bookings:
            if booking.status == 'CONFIRMED':
                return False

        return True

    async def update_status(
        self,
        booking_id: uuid.UUID,
        status: str,
        session: AsyncSession,
    ) -> Optional[Booking]:
        """Обновление статуса бронирования."""
        booking = await self.get(booking_id, session)
        if not booking:
            return None

        booking.status = status
        session.add(booking)
        await session.commit()
        await session.refresh(booking)
        return booking


booking_crud = CRUDBooking(Booking)
