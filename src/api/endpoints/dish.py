"""Эндпоинты блюд.

Модуль описывает маршруты управления блюдами кафе.

Маршруты:
   - `GET /` — список блюд;
   - `POST /` — создание блюда;
   - `GET /{dish_id}` — блюдо по ID;
   - `PATCH /{dish_id}` — обновление блюда.
"""

import uuid
from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api import error_responses as er
from src.api import validators as vt
from src.core.db import get_session
from src.models import Dish, User
from src.schemas import dish as schema
from src.services import dish_service

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get(
    '/',
    response_model=list[schema.DishInfo],
    responses=er.ERRORS_GET_MULTI_WITH_404,
)
async def get_multi(
    user: Annotated[User, Depends(vt.current_user_is_active)],
    session: SessionDep,
    cafe_id: uuid.UUID | None = Query(None),
    show_active: bool | None = Query(None),
) -> Sequence[Dish]:
    """GET `/dishes` - Получение списка блюд."""
    return await dish_service.get_multi_dishes(
        cafe_id=cafe_id,
        user=user,
        session=session,
        show_active=show_active,
    )


@router.post(
    '/',
    response_model=schema.DishInfo,
    status_code=status.HTTP_201_CREATED,
    responses=er.ERRORS_POST,
)
async def create(
    dish_create: schema.DishCreate,
    user: Annotated[User, Depends(vt.current_admin_or_manager)],
    session: SessionDep,
) -> Dish:
    """POST `/dishes` - Создает новое блюда."""
    return await dish_service.create_dish(
        dish_create=dish_create,
        user=user,
        session=session,
    )


@router.get(
    '/{dish_id}',
    response_model=schema.DishInfo,
    responses=er.ERRORS_4XX_FULL,
)
async def get_by_id(
    dish_id: uuid.UUID,
    user: Annotated[User, Depends(vt.current_user_is_active)],
    session: SessionDep,
) -> Dish:
    """GET `/dishes/{dish_id}` - Получение информации о блюде по его ID."""
    return await dish_service.get_dish_by_id(
        dish_id=dish_id,
        user=user,
        session=session,
    )


@router.patch(
    '/{dish_id}',
    response_model=schema.DishInfo,
    responses=er.ERRORS_4XX_FULL,
)
async def update(
    dish_id: uuid.UUID,
    dish_update: schema.DishUpdate,
    user: Annotated[User, Depends(vt.current_admin_or_manager)],
    session: SessionDep,
) -> Dish:
    """PATCH `/dishes/{dish_id}` - обновление информации о блюде по его ID."""
    return await dish_service.update_dish(
        dish_id=dish_id,
        dish_update=dish_update,
        user=user,
        session=session,
    )
