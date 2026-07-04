import uuid
from datetime import date
from typing import Optional

from sqlalchemy import exists, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.models import Booking, BookingStatus, User, UserRole


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
            select(self.model)
            .where(*filters)
            .order_by(
                self.model.booking_date.desc(),
            ),
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
            select(self.model)
            .where(*filters)
            .order_by(
                self.model.booking_date,
                self.model.slot_id,
            ),
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
            self.model.status.in_(
                [BookingStatus.PENDING, BookingStatus.CONFIRMED],
            ),
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
            self.model.status.in_(
                [BookingStatus.PENDING, BookingStatus.CONFIRMED],
            ),
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
            select(self.model)
            .where(*filters)
            .order_by(
                self.model.booking_date,
                self.model.slot_id,
            ),
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
        filters = [
            self.model.booking_date == booking_date,
            self.model.is_active.is_(True),
            self.model.status == BookingStatus.CONFIRMED,
            or_(
                self.model.table_id == table_id,
                self.model.slot_id == slot_id,
            ),
        ]
        if exclude_booking_id:
            filters.append(self.model.id != exclude_booking_id)

        query = select(exists().where(*filters))
        has_conflict = await session.scalar(query)
        return not bool(has_conflict)

    async def update_status(
        self,
        booking_id: uuid.UUID,
        status: str,
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
