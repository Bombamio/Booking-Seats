import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api import validators as vt
from src.core.db import get_session
from src.crud import cafe_crud, slot_crud
from src.models import User
from src.schemas import slot as schema

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get(
    '/',
    response_model=list[schema.TimeSlotInfo],
    response_model_exclude_none=True,
)
async def get_time_slots_list(  # noqa: ANN201
    cafe_id: uuid.UUID,
    user: Annotated[User, Depends(vt.current_user_is_active)],
    session: SessionDep,
    show_active: bool = True,
):
    """Получение списка доступных для бронирования временных слотов в кафе."""
    await vt.check_data_exists(
        crud=cafe_crud,
        data_id=cafe_id,
        session=session,
    )

    return await slot_crud.get_multi_by_cafe(
        cafe_id=cafe_id,
        session=session,
        show_active=show_active,
    )


@router.post(
    '/',
    response_model=schema.TimeSlotInfo,
    response_model_exclude_none=True,
)
async def create_time_slot(  # noqa: ANN201
    cafe_id: uuid.UUID,
    slot_create: schema.TimeSlotCreate,
    user: Annotated[User, Depends(vt.current_admin_or_manager)],
    session: SessionDep,
):
    """Создает новый временной слот в кафе."""
    cafe = await vt.check_data_exists(
        crud=cafe_crud,
        data_id=cafe_id,
        session=session,
    )
    await vt.check_data_is_active(
        crud=cafe_crud,
        data_id=cafe.id,
        session=session,
    )

    if user.role.MANAGER:
        await vt.check_cafe_managers(
            crud=cafe_crud,
            user=user,
            cafe_id=cafe.id,
            session=session,
        )

    await vt.check_slot_overlap(
        crud=slot_crud,
        cafe_id=cafe.id,
        start_time=slot_create.start_time,
        end_time=slot_create.end_time,
        session=session,
    )

    return await slot_crud.create_with_cafe(
        slot_create=slot_create,
        cafe_id=cafe.id,
        session=session,
    )


@router.get(
    '/{slot_id}',
    response_model=schema.TimeSlotInfo,
    response_model_exclude_none=True,
)
async def get_time_slot_by_id(  # noqa: ANN201
    cafe_id: uuid.UUID,
    slot_id: uuid.UUID,
    user: Annotated[User, Depends(vt.current_user_is_active)],
    session: SessionDep,
):
    """Получение информации о временном слоте в кафе по его ID."""
    await vt.check_data_exists(
        crud=cafe_crud,
        data_id=cafe_id,
        session=session,
    )
    slot = await vt.check_data_exists(
        crud=slot_crud,
        data_id=slot_id,
        session=session,
    )
    vt.check_belongs_to_cafe(data=slot, cafe_id=cafe_id)

    # Обычный пользователь видит только активные слоты.
    if not user.role.ADMIN and not user.role.MANAGER:
        await vt.check_data_is_active(
            crud=slot_crud,
            data_id=slot.id,
            session=session,
        )

    return slot


@router.patch(
    '/{slot_id}',
    response_model=schema.TimeSlotInfo,
    response_model_exclude_none=True,
)
async def update_time_slot(  # noqa: ANN201
    cafe_id: uuid.UUID,
    slot_id: uuid.UUID,
    slot_update: schema.TimeSlotUpdate,
    user: Annotated[User, Depends(vt.current_admin_or_manager)],
    session: SessionDep,
):
    """Обновление информации о временном слоте в кафе по его ID."""
    cafe = await vt.check_data_exists(
        crud=cafe_crud,
        data_id=cafe_id,
        session=session,
    )
    slot = await vt.check_data_exists(
        crud=slot_crud,
        data_id=slot_id,
        session=session,
    )
    vt.check_belongs_to_cafe(data=slot, cafe_id=cafe.id)

    if user.role.MANAGER:
        await vt.check_cafe_managers(
            crud=cafe_crud,
            user=user,
            cafe_id=cafe.id,
            session=session,
        )

    if slot_update.start_time is not None or slot_update.end_time is not None:
        await vt.check_slot_overlap(
            crud=slot_crud,
            cafe_id=cafe.id,
            start_time=slot_update.start_time or slot.start_time,
            end_time=slot_update.end_time or slot.end_time,
            session=session,
            exclude_id=slot.id,
        )

    return await slot_crud.update(
        db_entity=slot,
        update_data=slot_update,
        session=session,
    )
