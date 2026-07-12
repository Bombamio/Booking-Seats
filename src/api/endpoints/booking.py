import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api import error_responses as er
from src.api import validators as vt
from src.core.db import get_session
from src.models import User
from src.schemas import booking as schema
from src.services import booking_service

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get(
    '',
    response_model=list[schema.BookingInfo],
    response_model_exclude_none=True,
    responses=er.ERRORS_GET_MULTI,
    summary='Получение списка бронирований',
    description=(
        'Получение списка бронирований. Для администраторов и менеджеров - '
        'все бронирования (с возможностью выбора), для пользователей - '
        'только свои.'
    ),
)
async def get_booking_list(
    user: Annotated[User, Depends(vt.current_user_is_active)],
    session: SessionDep,
    show_active: Optional[bool] = Query(None),
    cafe_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
) -> list[schema.BookingInfo]:
    """Получение списка бронирований."""
    return await booking_service.get_multi_booking(
        user=user,
        session=session,
        show_active=show_active,
        cafe_id=cafe_id,
        user_id=user_id,
    )


@router.post(
    '',
    response_model=schema.BookingInfo,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
    responses=er.ERRORS_POST_BOOKING,
    summary='Создание нового бронирования',
    description='Создает новое бронирование. Только для авторизированных пользователей.',
)
async def create_booking(
    booking_create: schema.BookingCreate,
    user: Annotated[User, Depends(vt.current_user_is_active)],
    session: SessionDep,
) -> schema.BookingInfo:
    """Создание бронирования."""
    return await booking_service.create_booking(
        booking_create=booking_create,
        user=user,
        session=session,
    )


@router.get(
    '/{booking_id}',
    response_model=schema.BookingInfo,
    response_model_exclude_none=True,
    responses=er.ERRORS_4XX_FULL,
    summary='Получение информации о бронировании по его ID',
    description=(
        'Получение информации о бронировании по его ID. Для администраторов '
        'и менеджеров - все бронирования, для пользователей - только свои.'
    ),
)
async def get_booking(
    booking_id: uuid.UUID,
    user: Annotated[User, Depends(vt.current_user_is_active)],
    session: SessionDep,
) -> schema.BookingInfo:
    """Получение бронирования по ID."""
    return await booking_service.get_booking_by_id(
        booking_id=booking_id,
        user=user,
        session=session,
    )


@router.patch(
    '/{booking_id}',
    response_model=schema.BookingInfo,
    response_model_exclude_none=True,
    responses=er.ERRORS_4XX_FULL,
    summary='Обновление информации о бронировании по его ID',
    description=(
        'Обновление информации о бронировании по его ID. Для администраторов '
        'и менеджеров - все бронирования, для пользователей - только свои.'
    ),
)
async def update_booking(
    booking_id: uuid.UUID,
    booking_update: schema.BookingUpdate,
    user: Annotated[User, Depends(vt.current_user_is_active)],
    session: SessionDep,
) -> schema.BookingInfo:
    """Обновление бронирования по ID."""
    return await booking_service.update_booking(
        booking_id=booking_id,
        booking_update=booking_update,
        user=user,
        session=session,
    )
