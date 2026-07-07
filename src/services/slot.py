import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api import validators as vt
from src.core.db import get_session
from src.crud import cafe_crud, slot_crud
from src.models import Cafe, Slot, User, UserRole
from src.schemas.slot import TimeSlotCreate, TimeSlotUpdate

SessionDep = Annotated[AsyncSession, Depends(get_session)]


class SlotService:
    """Сервис для работы бизнес логики временных слотов."""

    def __init__(self, session: AsyncSession) -> None:
        """Сохранит сессию БД для операций сервиса."""
        self.session = session

    async def get_slots(
        self,
        cafe_id: uuid.UUID,
        show_active: bool,
    ) -> list[Slot]:
        """Возвращает список временных слотов кафе."""
        await self._get_cafe_or_404(cafe_id)
        return await slot_crud.get_multi_by_cafe(
            cafe_id=cafe_id,
            session=self.session,
            show_active=show_active,
        )

    async def get_slot(
        self,
        cafe_id: uuid.UUID,
        slot_id: uuid.UUID,
        user: User,
    ) -> Slot:
        """Возвращает временной слот по ID."""
        await self._get_cafe_or_404(cafe_id)
        slot = await self._get_slot_or_404(slot_id)
        vt.check_belongs_to_cafe(data=slot, cafe_id=cafe_id)

        if user.role == UserRole.USER:
            await vt.check_data_is_active(slot)

        return slot

    async def create_slot(
        self,
        cafe_id: uuid.UUID,
        slot_in: TimeSlotCreate,
        user: User,
    ) -> Slot:
        """Создаёт новый временной слот в кафе."""
        cafe = await self._validate_cafe_and_permissions(cafe_id, user)

        await vt.check_slot_overlap(
            crud=slot_crud,
            cafe_id=cafe.id,
            start_time=slot_in.start_time,
            end_time=slot_in.end_time,
            session=self.session,
        )

        return await slot_crud.create_with_cafe(
            slot_create=slot_in,
            cafe_id=cafe.id,
            session=self.session,
        )

    async def update_slot(
        self,
        cafe_id: uuid.UUID,
        slot_id: uuid.UUID,
        slot_in: TimeSlotUpdate,
        user: User,
    ) -> Slot:
        """Обновляет временной слот."""
        cafe = await self._validate_cafe_and_permissions(cafe_id, user)
        slot = await self._get_slot_or_404(slot_id)
        vt.check_belongs_to_cafe(data=slot, cafe_id=cafe.id)

        if slot_in.start_time is not None or slot_in.end_time is not None:
            await vt.check_slot_overlap(
                crud=slot_crud,
                cafe_id=cafe.id,
                start_time=slot_in.start_time or slot.start_time,
                end_time=slot_in.end_time or slot.end_time,
                session=self.session,
                exclude_id=slot.id,
            )

        return await slot_crud.update(
            db_entity=slot,
            update_data=slot_in,
            session=self.session,
        )

    async def _validate_cafe_and_permissions(
        self,
        cafe_id: uuid.UUID,
        user: User,
    ) -> Cafe:
        """Проверяет существование кафе, активность и права доступа менеджера.

        Используется в create_slot и update_slot во избежание дублирования кода.
        """
        cafe = await self._get_cafe_or_404(cafe_id)
        await vt.check_data_is_active(cafe)

        if user.role == UserRole.MANAGER:
            await vt.check_cafe_managers(user=user, cafes_id=[cafe.id])

        return cafe

    async def _get_cafe_or_404(self, cafe_id: uuid.UUID) -> Cafe:
        """Получает кафе по ID или возбуждает 404."""
        cafe = await cafe_crud.get(
            self.session,
            Cafe.id == cafe_id,
        )
        if cafe is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Кафе с id:{cafe_id} не найдено',
            )
        return cafe

    async def _get_slot_or_404(self, slot_id: uuid.UUID) -> Slot:
        """Получает слот по ID или возбуждает 404."""
        slot = await slot_crud.get(
            self.session,
            Slot.id == slot_id,
        )
        if slot is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Слот с id:{slot_id} не найден',
            )
        return slot


def get_slot_service(session: SessionDep) -> SlotService:
    """Функция для получения зависимости для SlotService."""
    return SlotService(session)
