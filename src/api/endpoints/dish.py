import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api import validators as vt
from src.core import constants as cs
from src.core.db import get_session
from src.core.decorators import with_error_responses
from src.models import Dish, User
from src.schemas import dish as schema
from src.services import dish_service

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get(
    '/',
    response_model=list[schema.DishInfo],
)
@with_error_responses(cs.ERRORS_GET_MULTI_WITH_404)
async def get_multi(
    cafe_id: Optional[uuid.UUID],
    user: Annotated[User, Depends(vt.current_user_is_active)],
    session: SessionDep,
    show_active: Optional[bool],
) -> list[Optional[Dish]]:
    """GET `/dishes` - Получение списка блюд."""
    return await dish_service.get_multi_dishes(
        cafe_id=cafe_id,
        user=user,
        session=session,
        show_active=show_active,
    )


@router.post(
    '/',
    response_model=[schema.DishInfo],
)
@with_error_responses(cs.ERRORS_POST)
async def create(
    obj_in: schema.DishCreate,
    user: Annotated[User, Depends(vt.current_admin_or_manager)],
    session: SessionDep,
) -> Dish:
    """POST `/dishes` - Создает новое блюда."""
    return await dish_service.create_dish(
        obj_in=obj_in,
        user=user,
        session=session,
    )


@router.get(
    '/{dish_id}',
    response_model=schema.DishInfo,
)
@with_error_responses(cs.ERRORS_4XX_FULL)
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
)
@with_error_responses(cs.ERRORS_4XX_FULL)
async def update(
    dish_id: uuid.UUID,
    obj_in: schema.DishUpdate,
    user: Annotated[User, Depends(vt.current_admin_or_manager)],
    session: SessionDep,
) -> Dish:
    """PATCH `/dishes/{dish_id}` - обновление информации о блюде по его ID."""
    return await dish_service.update_dish(
        dish_id=dish_id,
        obj_in=obj_in,
        user=user,
        session=session,
    )
