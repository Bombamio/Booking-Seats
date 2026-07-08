import uuid
from datetime import time
from typing import Annotated, Optional, Sequence

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_session
from src.crud import CRUDSlot, cafe_crud, slot_crud
from src.models import Cafe, Slot, User, UserRole
from src.schemas.slot import TimeSlotCreate, TimeSlotUpdate
from src.services.base import BaseService

SessionDep = Annotated[AsyncSession, Depends(get_session)]


class SlotService(CRUDSlot, BaseService):
    """Сервис для работы бизнес логики временных слотов."""

    def __init__(self, session: AsyncSession) -> None:
        """Сохранит сессию БД для операций сервиса."""
        self.session = session

    async def _check_slot_overlap(
        self,
        cafe_id: uuid.UUID,
        start_time: time,
        end_time: time,
        exclude_id: Optional[uuid.UUID] = None,
    ) -> None:
        """Проверяет пересечение временных слотов в кафе."""
        if await slot_crud.exists_overlapping(
            cafe_id=cafe_id,
            start_time=start_time,
            end_time=end_time,
            session=self.session,
            exclude_id=exclude_id,
        ):
            self.log_warning(f'Временной слот {start_time}-{end_time} пересекается с уже существующим.')
            self.raise_unprocessable_entity()

    async def get_slots(
        self,
        cafe_id: uuid.UUID,
        user: User,
        show_active: Optional[bool],
    ) -> Sequence[Slot]:
        """Возвращает список временных слотов кафе."""
        filters = []

        if cafe_id is not None:
            filters.append(Slot.cafe.any(Cafe.id == cafe_id))

        if user.role == UserRole.USER or show_active or user.role == UserRole.MANAGER and show_active is None:
            filters.append(Slot.is_active.is_(True))

        elif show_active is False and user.role == UserRole.MANAGER and cafe_id is not None:
            filters.append(
                Slot.cafe.any(Cafe.managers.any(User.id == user.id)),
            )

        elif user.role != UserRole.USER and show_active is not None:
            filters.append(Slot.is_active.is_(show_active))

        slots = await self.get_multi(
            session=self.session,
            *filters,
        )
        self.log_info(
            f'Пользователь {user.id} получил список из {len(slots)} временных слотов.',
        )
        return slots

    async def get_slot(
        self,
        cafe_id: uuid.UUID,
        slot_id: uuid.UUID,
        user: User,
    ) -> Slot:
        """Возвращает временной слот по ID."""
        filters = [Slot.id == slot_id]

        await self.ensure_exists(
            cafe_crud,
            self.session,
            Cafe.id == cafe_id,
        )
        filters.append(Slot.cafe.any(Cafe.id == cafe_id))

        if user.role == UserRole.USER:
            filters.append(Slot.is_active.is_(True))

        slot = await self.get_or_raise(
            slot_crud,
            self.session,
            *filters,
        )

        self.log_info(f'Пользователь {user.id} получил информацию о временном слоте {slot_id}')
        return slot

    async def create_slot(
        self,
        cafe_id: uuid.UUID,
        slot_in: TimeSlotCreate,
        user: User,
    ) -> Slot:
        """Создаёт новый временной слот в кафе."""
        await self.ensure_manager_cafe_access(
            user=user,
            cafe_id=cafe_id,
        )

        cafe = await self.get_or_raise(
            cafe_crud,
            self.session,
            Cafe.id == cafe_id,
            Cafe.is_active.is_(True),
        )

        await self._check_slot_overlap(
            cafe_id=cafe_id,
            start_time=slot_in.start_time,
            end_time=slot_in.end_time,
        )

        result = await self.create(
            create_data=slot_in,
            session=self.session,
            cafe=cafe,
        )
        self.log_info(
            f'Пользователь {user.id} создал временной слот на время {slot_in.start_time}-{slot_in.end_time}',
        )
        return result

    async def update_slot(
        self,
        cafe_id: uuid.UUID,
        slot_id: uuid.UUID,
        slot_in: TimeSlotUpdate,
        user: User,
    ) -> Slot:
        """Обновляет временной слот."""
        await self.ensure_manager_cafe_access(
            user=user,
            cafe_id=cafe_id,
        )

        cafe = await self.get_or_raise(
            cafe_crud,
            self.session,
            Cafe.id == cafe_id,
        )
        slot = await self.get_or_raise(
            slot_crud,
            self.session,
            Slot.cafe.any(Cafe.id == cafe_id),
            Slot.id == slot_id,
        )

        if slot_in.start_time is not None or slot_in.end_time is not None:
            await self._check_slot_overlap(
                cafe_id=cafe_id,
                start_time=slot_in.start_time or slot.start_time,
                end_time=slot_in.end_time or slot.end_time,
                exclude_id=slot_id,
            )

        result = await slot_crud.update(
            db_entity=slot,
            update_data=slot_in,
            session=self.session,
            cafe=cafe,
        )
        self.log_info(f'Пользователь {user.id} изменил информацию о временном слоте {slot_id}.')
        return result


def get_slot_service(session: SessionDep) -> SlotService:
    """Функция для получения зависимости для SlotService."""
    return SlotService(session)
