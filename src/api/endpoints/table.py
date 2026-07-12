"""Эндпоинты столиков.

Модуль описывает маршруты управления столиками кафе.

Маршруты:
   - `GET /` — список столов кафе;
   - `POST /` — создание стола;
   - `GET /{table_id}` — стол по ID;
   - `PATCH /{table_id}` — обновление стола.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api import error_responses as er
from src.api import validators as vt
from src.api.openapi_examples import (
    SUCCESS_TABLES_LIST,
    SUCCESS_TABLE_CREATED,
    SUCCESS_TABLE_INFO,
    merge_responses,
)
from src.core.db import get_session
from src.models import User
from src.schemas import table as schema
from src.services import table_service

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get(
    '',
    response_model=list[schema.TableInfo],
    response_model_exclude_none=True,
    summary='Получение списка столов в кафе',
    responses=merge_responses(SUCCESS_TABLES_LIST, er.ERRORS_GET_MULTI_WITH_404),
    description=(
        'Получение списка доступных для бронирования столов в кафе.'
        'Для администраторов и менеджеров - все столы (с возможностью выбора),'
        'для пользователей - только активные.'
    ),
)
async def get_tables_list(
    cafe_id: uuid.UUID,
    user: Annotated[User, Depends(vt.current_user_is_active)],
    session: SessionDep,
    show_active: bool | None = Query(None),
) -> list[schema.TableInfo]:
    """Получение списка столиков в кафе."""
    return await table_service.get_multi_by_cafe(
        cafe_id=cafe_id,
        session=session,
        user=user,
        show_active=show_active,
    )


@router.post(
    '',
    response_model=schema.TableInfo,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
    summary='Новый стол в кафе',
    responses=merge_responses(SUCCESS_TABLE_CREATED, er.ERRORS_4XX_FULL),
    description=('Создает новый стол кафе.Только для администраторов и менеджеров.'),
)
async def create_table(
    cafe_id: uuid.UUID,
    table_create: schema.TableCreate,
    user: Annotated[User, Depends(vt.current_admin_or_manager)],
    session: SessionDep,
) -> schema.TableInfo:
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
    responses=merge_responses(SUCCESS_TABLE_INFO, er.ERRORS_4XX_FULL),
    description=(
        'Получение информации о столе в кафе по его ID.'
        'Для администраторов и менеджеров - все столы,'
        'для пользователей - только активные.'
    ),
)
async def get_table(
    cafe_id: uuid.UUID,
    table_id: uuid.UUID,
    user: Annotated[User, Depends(vt.current_user_is_active)],
    session: SessionDep,
) -> schema.TableInfo:
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
    responses=merge_responses(SUCCESS_TABLE_INFO, er.ERRORS_4XX_FULL),
    description=('Обновление информации о столе в кафе по его ID.Только для администраторов и менеджеров.'),
)
async def update_table(
    cafe_id: uuid.UUID,
    table_id: uuid.UUID,
    table_update: schema.TableUpdate,
    user: Annotated[User, Depends(vt.current_admin_or_manager)],
    session: SessionDep,
) -> schema.TableInfo:
    """Обновление информации о столике в кафе по его ID."""
    return await table_service.update_table(
        cafe_id=cafe_id,
        table_id=table_id,
        table_update=table_update,
        session=session,
        user=user,
    )
