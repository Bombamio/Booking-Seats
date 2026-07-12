import uuid
from datetime import date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import src.schemas as schema
from src.core.celery_dispatch import dispatch_celery_task, revoke_celery_task
from src.core.exceptions import BookingSeatsCeleryError
from src.core.settings import settings
from src.crud import CRUDBooking, booking_crud, cafe_crud, dish_crud, slot_crud, table_crud, user_crud
from src.models import (
    Booking,
    BookingDish,
    BookingItem,
    BookingStatus,
    Cafe,
    Dish,
    Slot,
    Table,
    User,
    UserRole,
)
from src.services.base import BaseService
from src.tasks.notifications import notify_admin
from src.tasks.reminders import send_reminder


class BookingService(CRUDBooking, BaseService):
    """Обработает операции с бронированиями."""

    @staticmethod
    def _to_booking_info(booking: Booking) -> schema.BookingInfo:
        """Соберет схему ответа бронирования со связанными объектами."""
        return schema.BookingInfo(
            id=booking.id,
            user=schema.UserShortInfo.model_validate(booking.user, from_attributes=True),
            cafe=schema.CafeShortInfo.model_validate(booking.cafe, from_attributes=True),
            tables_slots=[
                schema.BookingTableSlotShortInfo(
                    table=schema.TableShortInfo.model_validate(
                        item.table,
                        from_attributes=True,
                    ),
                    slot=schema.TimeSlotShortInfo.model_validate(
                        item.slot,
                        from_attributes=True,
                    ),
                )
                for item in booking.booking_items
            ],
            preordered_dishes=[
                schema.BookingDishInfo(
                    dish=schema.DishInfo.model_validate(item.dish, from_attributes=True),
                    quantity=item.quantity,
                )
                for item in booking.booking_dishes
            ],
            guest_number=booking.guest_number,
            note=booking.note,
            status=booking.status,
            booking_date=booking.booking_date,
            is_active=booking.is_active,
            created_at=booking.created_at,
            updated_at=booking.updated_at,
        )

    def _pairs_from_tables_slots(
        self,
        tables_slots: list[schema.BookingTableSlotCreate],
    ) -> list[tuple[uuid.UUID, uuid.UUID]]:
        """Вернет уникальные пары стол-слот из входной схемы."""
        pairs = [(item.table_id, item.slot_id) for item in tables_slots]
        if len(pairs) != len(set(pairs)):
            self.raise_unprocessable_entity('Пары стол-слот не должны повторяться.')
        return pairs

    @staticmethod
    def _pairs_from_booking_items(
        booking_items: list[BookingItem],
    ) -> list[tuple[uuid.UUID, uuid.UUID]]:
        """Вернет пары стол-слот из связанных элементов бронирования."""
        return [(item.table_id, item.slot_id) for item in booking_items]

    @staticmethod
    def _table_ids_from_booking_items(
        booking_items: list[BookingItem],
    ) -> set[uuid.UUID]:
        """Вернет ID столов из связанных элементов бронирования."""
        return {item.table_id for item in booking_items}

    def _dish_quantities_from_preorder(
        self,
        preordered_dishes: list[schema.BookingDishCreate],
    ) -> dict[uuid.UUID, int]:
        """Вернет количества блюд из предзаказа."""
        dish_quantities = {item.dish_id: item.quantity for item in preordered_dishes}
        if len(dish_quantities) != len(preordered_dishes):
            self.raise_unprocessable_entity('Блюда в предзаказе не должны повторяться.')
        return dish_quantities

    async def _get_booking_or_raise(
        self,
        booking_id: uuid.UUID,
        session: AsyncSession,
    ) -> Booking:
        """Вернет бронирование со связями или сообщит 404."""
        booking = await booking_crud.get_with_details(
            session,
            Booking.id == booking_id,
        )
        if booking is None:
            self.raise_not_found()
        return booking

    async def _ensure_booking_access(
        self,
        booking: Booking,
        user: User,
    ) -> None:
        """Проверит доступ пользователя к бронированию."""
        if user.role == UserRole.ADMIN:
            return
        if user.role == UserRole.MANAGER:
            if user.cafe_id == booking.cafe_id:
                return
            self.raise_forbidden()
        if booking.user_id != user.id:
            self.raise_forbidden()

    async def _validate_cafe(
        self,
        cafe_id: uuid.UUID,
        user: User,
        session: AsyncSession,
    ) -> Cafe:
        """Проверит существование, активность кафе и доступ менеджера."""
        await self.ensure_ids_exist(cafe_crud, session, cafe_id)
        cafe = await cafe_crud.get(
            session,
            Cafe.id == cafe_id,
        )
        await self.ensure_is_active(cafe)
        await self.ensure_manager_cafe_access(user, cafe.id)
        return cafe

    async def _validate_tables_slots(
        self,
        cafe_id: uuid.UUID,
        tables_slots: list[schema.BookingTableSlotCreate],
        booking_date: date,
        session: AsyncSession,
        exclude_booking_id: uuid.UUID | None = None,
    ) -> tuple[list[tuple[uuid.UUID, uuid.UUID]], list[Table]]:
        """Проверит существование, принадлежность кафе и доступность пар."""
        pairs = self._pairs_from_tables_slots(tables_slots)

        table_ids = {table_id for table_id, _ in pairs}
        slot_ids = {slot_id for _, slot_id in pairs}

        await self.ensure_ids_exist(
            table_crud,
            session,
            dict(pairs),
            related_crud=slot_crud,
        )

        tables = await table_crud.get_multi(
            session,
            Table.id.in_(table_ids),
        )
        slots = await slot_crud.get_multi(
            session,
            Slot.id.in_(slot_ids),
        )

        table_from_other_cafe = any(table.cafe_id != cafe_id for table in tables)
        slot_from_other_cafe = any(slot.cafe_id != cafe_id for slot in slots)
        if table_from_other_cafe or slot_from_other_cafe:
            self.raise_not_found()

        if any(not table.is_active for table in tables) or any(not slot.is_active for slot in slots):
            self.raise_unprocessable_entity()

        has_conflicts = await booking_crud.has_table_slot_conflicts(
            tables_slots=pairs,
            booking_date=booking_date,
            session=session,
            exclude_booking_id=exclude_booking_id,
        )
        if has_conflicts:
            self.raise_unprocessable_entity('Выбранный стол уже забронирован на этот слот.')

        return pairs, list(tables)

    def _ensure_tables_capacity(
        self,
        tables: list[Table],
        guest_number: int,
    ) -> None:
        """Проверит, что выбранные столы вмещают всех гостей."""
        seats_count = sum(table.seat_number for table in tables)
        if seats_count < guest_number:
            self.raise_unprocessable_entity(
                'Количество гостей превышает вместимость выбранных столов.',
            )

    async def _get_tables_by_ids(
        self,
        table_ids: set[uuid.UUID],
        session: AsyncSession,
    ) -> list[Table]:
        """Вернет столы по ID."""
        await self.ensure_ids_exist(table_crud, session, list(table_ids))
        return list(await table_crud.get_multi(session, Table.id.in_(table_ids)))

    async def _build_booking_dishes(
        self,
        cafe_id: uuid.UUID,
        preordered_dishes: list[schema.BookingDishCreate],
        session: AsyncSession,
    ) -> list[BookingDish]:
        """Проверит блюда и вернет позиции предзаказа."""
        dish_quantities = self._dish_quantities_from_preorder(preordered_dishes)
        if not dish_quantities:
            return []

        await self.ensure_ids_exist(
            dish_crud,
            session,
            list(dish_quantities.keys()),
        )

        result = await session.execute(
            select(Dish).options(selectinload(Dish.cafes)).where(Dish.id.in_(dish_quantities)),
        )
        dishes = list(result.scalars().all())

        for dish in dishes:
            dish_cafe_ids = {cafe.id for cafe in dish.cafes}
            if not dish.is_active or cafe_id not in dish_cafe_ids:
                self.raise_unprocessable_entity()

        return [
            BookingDish(
                dish_id=dish.id,
                quantity=dish_quantities[dish.id],
            )
            for dish in dishes
        ]

    async def get_multi_booking(
        self,
        user: User,
        session: AsyncSession,
        show_active: bool = True,
        cafe_id: uuid.UUID | None = None,
        user_id: uuid.UUID | None = None,
    ) -> list[schema.BookingInfo]:
        """Вернет список бронирований с учетом роли пользователя."""
        if cafe_id is not None:
            await self.ensure_ids_exist(cafe_crud, session, cafe_id)
        if user_id is not None:
            await self.ensure_ids_exist(user_crud, session, user_id)

        filters = []

        if user.role == UserRole.USER:
            filters.append(Booking.user_id == user.id)
            filters.append(Booking.is_active.is_(True))
            if cafe_id is not None:
                filters.append(Booking.cafe_id == cafe_id)
        else:
            if user.role == UserRole.MANAGER:
                if user.cafe_id is None:
                    self.raise_forbidden()
                filters.append(Booking.cafe_id == user.cafe_id)
            elif cafe_id is not None:
                filters.append(Booking.cafe_id == cafe_id)

            if user_id is not None:
                filters.append(Booking.user_id == user_id)

            if show_active:
                filters.append(Booking.is_active.is_(True))

        bookings = await booking_crud.get_multi_with_details(session, *filters)
        self.log_info(
            f'Пользователь {user.id} получил список из {len(bookings)} бронирований.',
        )
        return [self._to_booking_info(booking) for booking in bookings]

    async def create_booking(
        self,
        booking_create: schema.BookingCreate,
        user: User,
        session: AsyncSession,
    ) -> schema.BookingInfo:
        """Создаст новое бронирование."""
        if booking_create.booking_date < date.today():
            self.raise_unprocessable_entity(
                'Нельзя забронировать на прошедшую дату.',
            )

        await self._validate_cafe(
            cafe_id=booking_create.cafe_id,
            user=user,
            session=session,
        )
        pairs, tables = await self._validate_tables_slots(
            cafe_id=booking_create.cafe_id,
            tables_slots=booking_create.tables_slots,
            booking_date=booking_create.booking_date,
            session=session,
        )
        self._ensure_tables_capacity(
            tables=tables,
            guest_number=booking_create.guest_number,
        )
        booking_dishes = await self._build_booking_dishes(
            cafe_id=booking_create.cafe_id,
            preordered_dishes=booking_create.pre_ordered_dishes or [],
            session=session,
        )

        booking = Booking(
            user_id=user.id,
            cafe_id=booking_create.cafe_id,
            booking_date=booking_create.booking_date,
            guest_number=booking_create.guest_number,
            note=booking_create.note,
            booking_dishes=booking_dishes,
            booking_items=[
                BookingItem(
                    table_id=table_id,
                    slot_id=slot_id,
                )
                for table_id, slot_id in pairs
            ],
        )
        session.add(booking)
        await session.commit()

        created_booking = await self._get_booking_or_raise(booking.id, session)
        self.log_info(
            f'Пользователь {user.id} создал бронирование {booking.id}.',
        )
        try:
            reminder_task_id = self._enqueue_booking_tasks(created_booking)
            if reminder_task_id:
                created_booking.reminder_task_id = reminder_task_id
                session.add(created_booking)
                await session.commit()
        except BookingSeatsCeleryError as exc:
            self.log_warning(
                f'Бронирование {booking.id} создано, но фоновые задачи не поставлены: {exc.message}',
            )
        return self._to_booking_info(created_booking)

    @staticmethod
    def _format_booking_slot_times(booking: Booking) -> str:
        """Вернёт человекочитаемое время слотов бронирования."""
        slot_labels = [
            f'{item.slot.start_time.strftime("%H:%M")}-{item.slot.end_time.strftime("%H:%M")}'
            for item in booking.booking_items
        ]
        return ', '.join(slot_labels) if slot_labels else 'не указано'

    def _enqueue_booking_notifications(self, booking: Booking, event_type: str) -> None:
        """Поставит уведомления менеджерам кафе о событии бронирования."""
        slot_times = self._format_booking_slot_times(booking)
        for manager in booking.cafe.managers:
            if not manager.email:
                self.log_warning(
                    f'Менеджер {manager.id} кафе {booking.cafe_id} без email — уведомление пропущено.',
                )
                continue
            dispatch_celery_task(
                lambda manager=manager: notify_admin.delay(
                    event_type=event_type,
                    cafe_name=booking.cafe.name,
                    booking_id=str(booking.id),
                    booking_date=str(booking.booking_date),
                    slot_times=slot_times,
                    admin_email=manager.email,
                    username=booking.user.username,
                    user_email=booking.user.email,
                    user_phone=booking.user.phone,
                ),
            )

    def _enqueue_booking_reminder(self, booking: Booking) -> str | None:
        """Поставит напоминание пользователю о бронировании."""
        if not booking.booking_items:
            return None

        slot_start = booking.booking_items[0].slot.start_time
        booking_start = datetime.combine(booking.booking_date, slot_start)
        time_reminder = booking_start - timedelta(minutes=settings.reminder_minutes_before)
        reminder_result = dispatch_celery_task(
            lambda: send_reminder.apply_async(
                kwargs={
                    'cafe_name': booking.cafe.name,
                    'booking_date': str(booking.booking_date),
                    'slot_times': self._format_booking_slot_times(booking),
                    'username': booking.user.username,
                    'user_email': booking.user.email,
                },
                eta=time_reminder,
            ),
        )
        return reminder_result.id

    def _enqueue_booking_tasks(self, created_booking: Booking) -> str | None:
        """Поставит уведомления и напоминания о бронировании в очередь Celery."""
        self._enqueue_booking_notifications(created_booking, 'created')
        return self._enqueue_booking_reminder(created_booking)

    def _cancel_booking_reminder(self, booking: Booking) -> None:
        """Отзовёт отложенное напоминание о бронировании."""
        if not booking.reminder_task_id:
            return
        try:
            revoke_celery_task(booking.reminder_task_id)
        except BookingSeatsCeleryError as exc:
            self.log_warning(
                f'Напоминание {booking.reminder_task_id} для бронирования {booking.id} '
                f'не отозвано: {exc.message}',
            )
        booking.reminder_task_id = None

    async def get_booking_by_id(
        self,
        booking_id: uuid.UUID,
        user: User,
        session: AsyncSession,
    ) -> schema.BookingInfo:
        """Вернет бронирование по ID с учетом роли пользователя."""
        booking = await self._get_booking_or_raise(booking_id, session)
        await self._ensure_booking_access(booking, user)
        self.log_info(
            f'Пользователь {user.id} получил бронирование {booking_id}.',
        )
        return self._to_booking_info(booking)

    async def update_booking(  # noqa: C901
        self,
        booking_id: uuid.UUID,
        booking_update: schema.BookingUpdate,
        user: User,
        session: AsyncSession,
    ) -> schema.BookingInfo:
        """Обновит бронирование по ID."""
        booking = await self._get_booking_or_raise(booking_id, session)
        await self._ensure_booking_access(booking, user)

        if booking.booking_date < date.today():
            self.raise_unprocessable_entity(
                'Нельзя изменить бронирование на прошедшую дату.',
            )

        updated_fields = booking_update.model_fields_set
        update_data = booking_update.model_dump(exclude_unset=True)
        tables_slots = booking_update.tables_slots if 'tables_slots' in updated_fields else None
        preordered_dishes = (
            booking_update.pre_ordered_dishes if 'pre_ordered_dishes' in updated_fields else None
        )
        update_data.pop('tables_slots', None)
        update_data.pop('pre_ordered_dishes', None)
        booking_date_updated = 'booking_date' in update_data
        guest_number = update_data.get('guest_number', booking.guest_number)
        deactivate = update_data.get('is_active') is False
        capacity_check_needed = tables_slots is not None or 'guest_number' in update_data
        tables_for_capacity: list[Table] | None = None

        if tables_slots is None and booking_date_updated:
            pairs = self._pairs_from_booking_items(booking.booking_items)
            booking_date = update_data['booking_date']
            has_conflicts = await booking_crud.has_table_slot_conflicts(
                tables_slots=pairs,
                booking_date=booking_date,
                session=session,
                exclude_booking_id=booking.id,
            )
            if has_conflicts:
                self.raise_unprocessable_entity('Выбранный стол уже забронирован на этот слот.')

        if tables_slots is not None:
            booking_date = update_data.get('booking_date', booking.booking_date)
            pairs, tables_for_capacity = await self._validate_tables_slots(
                cafe_id=booking.cafe_id,
                tables_slots=tables_slots,
                booking_date=booking_date,
                session=session,
                exclude_booking_id=booking.id,
            )
            await booking_crud.replace_booking_items(booking, pairs, session)

        if preordered_dishes is not None:
            booking.booking_dishes = await self._build_booking_dishes(
                cafe_id=booking.cafe_id,
                preordered_dishes=preordered_dishes,
                session=session,
            )

        if capacity_check_needed and not deactivate:
            if tables_for_capacity is None:
                tables_for_capacity = await self._get_tables_by_ids(
                    self._table_ids_from_booking_items(booking.booking_items),
                    session,
                )
            self._ensure_tables_capacity(
                tables=tables_for_capacity,
                guest_number=guest_number,
            )

        update_data.pop('is_active', None)
        for field, value in update_data.items():
            setattr(booking, field, value)

        if deactivate:
            self._cancel_booking_reminder(booking)
            booking.status = BookingStatus.CANCELED
            await self.soft_delete(booking, session)

        session.add(booking)
        await session.commit()

        updated_booking = await self._get_booking_or_raise(booking.id, session)
        self.log_info(
            f'Пользователь {user.id} обновил бронирование {booking_id}.',
        )
        try:
            event_type = 'canceled' if deactivate else 'updated'
            self._enqueue_booking_notifications(updated_booking, event_type)
        except BookingSeatsCeleryError as exc:
            self.log_warning(
                f'Бронирование {booking_id} обновлено, но уведомления не поставлены: {exc.message}',
            )
        return self._to_booking_info(updated_booking)


booking_service = BookingService(Booking)
