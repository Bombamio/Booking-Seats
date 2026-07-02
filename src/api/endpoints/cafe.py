import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api import validators as vt
from models import User
from schemas import CafeCreate, CafeInfo, CafeUpdate
from services.cafe import CafeService

from core.db import get_session

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_session)]
cafe_service = CafeService()


@router.get(
    '/',
    response_model=list[CafeInfo],
    summary='Получение списка кафе',
)
async def get_cafes(
    session: SessionDep,
    user: Annotated[User, Depends(vt.current_user_is_active)],
    show_active: bool = True,
) -> list[CafeInfo]:
    """Получение списка кафе.

    Для администраторов и менеджеров - все кафе (с возможностью выбора),
    для пользователей - только активные.
    """
    return await cafe_service.get_cafes(session, user, show_active)


@router.post(
    '/',
    response_model=CafeInfo,
    summary='Создание нового кафе',
    dependencies=[Depends(vt.current_admin_or_manager)],
)
async def create_cafe(
    cafe: CafeCreate,
    session: SessionDep,
) -> CafeInfo:
    """Создает новое кафе.

    Только для администраторов и менеджеров.
    """
    return await cafe_service.create_cafe(session, cafe)


@router.get(
    '/{cafe_id}',
    response_model=CafeInfo,
    summary='Получение информации о кафе по его ID',
)
async def get_cafe(
    cafe_id: uuid.UUID,
    session: SessionDep,
    user: Annotated[User, Depends(vt.current_user_is_active)],
) -> CafeInfo:
    """Получение информации о кафе по его ID.

    Для администраторов и менеджеров - все кафе, для пользователей
    только активные.
    """
    return await cafe_service.get_cafe(session, cafe_id, user)


@router.patch(
    '/{cafe_id}',
    response_model=CafeInfo,
    summary='Обновление информации о кафе по его ID',
    dependencies=[Depends(vt.current_admin_or_manager)],
)
async def update_cafe(
    cafe_id: uuid.UUID,
    cafe: CafeUpdate,
    session: SessionDep,
) -> CafeInfo:
    """Обновление информации о кафе по его ID.

    Только для администраторов и менеджеров.
    """
    return await cafe_service.update_cafe(session, cafe, cafe_id)
