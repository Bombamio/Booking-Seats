import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api import validators as vt
from src.core.constants import (
    ERRORS_4XX_FULL,
    ERRORS_GET_MULTI_WITH_404,
)
from src.core.db import get_session
from src.core.decorators import with_error_responses
from src.models import Table, User
from src.schemas import table as schema
from src.services import table_service

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get(
    '/',
    response_model=list[schema.TableInfo],
    response_model_exclude_none=True,
    summary='Получение списка столов в кафе',
    description=(
        'Получение списка доступных для бронирования столов в кафе.'
        'Для администраторов и менеджеров - все столы (с возможностью выбора),'
        'для пользователей - только активные.'
    ),
)
@with_error_responses(ERRORS_GET_MULTI_WITH_404)
async def get_tables_list(
    cafe_id: uuid.UUID,
    user: Annotated[User, Depends(vt.current_user)],
    session: SessionDep,
    show_active: bool = True,
) -> list[Table]:
    """Получение списка столиков в кафе."""
    return await table_service.get_multi_by_cafe(
        cafe_id=cafe_id,
        session=session,
        user=user,
        show_active=show_active,
    )


@router.post(
    '/',
    response_model=schema.TableInfo,
    response_model_exclude_none=True,
    summary='Новый стол в кафе',
    description=(
        'Создает новый стол кафе.'
        'Только для администраторов и менеджеров.'
    ),
)
@with_error_responses(ERRORS_4XX_FULL)
async def create_table(
    cafe_id: uuid.UUID,
    table_create: schema.TableCreate,
    user: Annotated[User, Depends(vt.current_admin_or_manager)],
    session: SessionDep,
) -> Table:
    """Создание столика."""
    return await table_service.create_with_cafe(
        cafe_id=cafe_id,
        table_create=table_create,
        session=session,
        user=user,
    )


@router.get(
    '/{table_id}',
    response_model=schema.TableInfo,
    response_model_exclude_none=True,
    summary='Информация о столе в кафе по его ID',
    description=(
        'Получение информации о столе в кафе по его ID.'
        'Для администраторов и менеджеров - все столы,'
        'для пользователей - только активные.'
    ),
)
@with_error_responses(ERRORS_4XX_FULL)
async def get_table(
    cafe_id: uuid.UUID,
    table_id: uuid.UUID,
    user: Annotated[User, Depends(vt.current_user)],
    session: SessionDep,
) -> Table:
    """Получение столика по ID."""
    return await table_service.get_by_cafe_and_id(
        cafe_id=cafe_id,
        table_id=table_id,
        session=session,
        user=user,
    )


@router.patch(
    '/{table_id}',
    response_model=schema.TableInfo,
    response_model_exclude_none=True,
    summary='Обновление информации о столе в кафе по его ID',
    description=(
        'Обновление информации о столе в кафе по его ID.'
        'Только для администраторов и менеджеров.'
    ),
)
@with_error_responses(ERRORS_4XX_FULL)
async def update_table(
    cafe_id: uuid.UUID,
    table_id: uuid.UUID,
    table_update: schema.TableUpdate,
    user: Annotated[User, Depends(vt.current_admin_or_manager)],
    session: SessionDep,
) -> Table:
    """Обновление информации о столике в кафе по его ID."""
    return await table_service.update_table(
        cafe_id=cafe_id,
        table_id=table_id,
        table_update=table_update,
        session=session,
        user=user,
    )
