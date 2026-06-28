import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api import validators as vt
from src.core.db import get_session
from src.models import User
from src.schemas import CafeCreate, CafeInfo, CafeUpdate
from src.services.cafe import CafeService, get_cafe_service

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_session)]
CafeServiceDep = Annotated[CafeService, Depends(get_cafe_service)]


@router.get(
    '/',
    response_model=list[CafeInfo],
    summary='Получение списка кафе',
)
async def get_cafes(
    service: CafeServiceDep,
    user: Annotated[User, Depends(vt.current_user)],
    show_active: bool = True,
) -> list[CafeInfo]:
    """Получение списка кафе.

    Для администраторов и менеджеров - все кафе (с возможностью выбора),
    для пользователей - только активные.
    """
    return await service.get_cafes(user, show_active)


@router.post(
    '/',
    response_model=CafeInfo,
    summary='Создание нового кафе',
    dependencies=[Depends(vt.current_admin_or_manager)],
)
async def create_cafe(
    cafe: CafeCreate,
    service: CafeServiceDep,
) -> CafeInfo:
    """Создает новое кафе.

    Только для администраторов и менеджеров.
    """
    return await service.create_cafe(cafe)


@router.get(
    '/{cafe_id}',
    response_model=CafeInfo,
    summary='Получение информации о кафе по его ID',
)
async def get_cafe(
    cafe_id: uuid.UUID,
    service: CafeServiceDep,
    user: Annotated[User, Depends(vt.current_user)],
) -> CafeInfo:
    """Получение информации о кафе по его ID.

    Для администраторов и менеджеров - все кафе, для пользователей
    только активные.
    """
    return await service.get_cafe(cafe_id, user)


@router.patch(
    '/{cafe_id}',
    summary='Обновление информации о кафе по его ID',
    dependencies=[Depends(vt.current_admin_or_manager)],
)
async def update_cafe(
    cafe_id: uuid.UUID,
    cafe: CafeUpdate,
    service: CafeServiceDep,
) -> CafeInfo:
    """Обновление информации о кафе по его ID.

    Только для администраторов и менеджеров.
    """
    return await service.update_cafe(cafe_id, cafe)
