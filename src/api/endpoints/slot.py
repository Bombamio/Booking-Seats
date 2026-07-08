import uuid
from typing import Annotated, Optional, Sequence

from fastapi import APIRouter, Depends, status

from src.api import error_responses as er
from src.api import validators as vt
from src.models import Slot, User
from src.schemas import slot as schema
from src.services.slot import SlotService, get_slot_service

router = APIRouter()

SlotServiceDep = Annotated[SlotService, Depends(get_slot_service)]


@router.get(
    '/',
    response_model=list[schema.TimeSlotInfo],
    summary='Получение списка временных слотов кафе',
    responses=er.ERRORS_GET_MULTI_WITH_404,
)
async def get_time_slots_list(
    cafe_id: uuid.UUID,
    service: SlotServiceDep,
    user: Annotated[User, Depends(vt.current_user_is_active)],
    show_active: Optional[bool],
) -> Sequence[Slot]:
    """Получение списка доступных для бронирования временных слотов в кафе."""
    return await service.get_slots(cafe_id, user, show_active)


@router.post(
    '/',
    response_model=schema.TimeSlotInfo,
    summary='Создание нового временного слота в кафе',
    status_code=status.HTTP_201_CREATED,
    responses=er.ERRORS_4XX_FULL,
)
async def create_time_slot(
    cafe_id: uuid.UUID,
    slot_in: schema.TimeSlotCreate,
    service: SlotServiceDep,
    user: Annotated[User, Depends(vt.current_admin_or_manager)],
) -> Slot:
    """Создает новый временной слот в кафе."""
    return await service.create_slot(cafe_id, slot_in, user)


@router.get(
    '/{slot_id}',
    response_model=schema.TimeSlotInfo,
    summary='Получение информации о временном слоте по его ID',
    responses=er.ERRORS_4XX_FULL,
)
async def get_time_slot_by_id(
    cafe_id: uuid.UUID,
    slot_id: uuid.UUID,
    service: SlotServiceDep,
    user: Annotated[User, Depends(vt.current_user_is_active)],
) -> Slot:
    """Получение информации о временном слоте в кафе по его ID."""
    return await service.get_slot(cafe_id, slot_id, user)


@router.patch(
    '/{slot_id}',
    response_model=schema.TimeSlotInfo,
    summary='Обновление информации о временном слоте по его ID',
    responses=er.ERRORS_4XX_FULL,
)
async def update_time_slot(
    cafe_id: uuid.UUID,
    slot_id: uuid.UUID,
    slot_in: schema.TimeSlotUpdate,
    service: SlotServiceDep,
    user: Annotated[User, Depends(vt.current_admin_or_manager)],
) -> Slot:
    """Обновление информации о временном слоте в кафе по его ID."""
    return await service.update_slot(cafe_id, slot_id, slot_in, user)
