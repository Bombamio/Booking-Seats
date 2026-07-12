"""Эндпоинты акций.

Модуль описывает маршруты управления акциями кафе.

Маршруты:
   - `GET /` — список акций;
   - `POST /` — создание акции;
   - `GET /{action_id}` — акция по ID;
   - `PATCH /{action_id}` — обновление акции.
"""

import uuid
from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api import error_responses as er
from src.api import validators as vt
from src.core.db import get_session
from src.models import Action, User
from src.schemas import ActionCreate, ActionInfo, ActionUpdate
from src.services import action_service

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get(
    '/',
    response_model=list[ActionInfo],
    responses=er.ERRORS_GET_MULTI,
)
async def get_actions(
    session: SessionDep,
    user: Annotated[User, Depends(vt.current_user_is_active)],
    show_active: bool | None = Query(None),
    cafe_id: uuid.UUID | None = Query(None),
) -> Sequence[Action]:
    """Вернет список акций с фильтрацией."""
    return await action_service.get_actions(
        session=session,
        user=user,
        show_active=show_active,
        cafe_id=cafe_id,
    )


@router.post(
    '/',
    response_model=ActionInfo,
    status_code=status.HTTP_201_CREATED,
    responses=er.ERRORS_POST,
)
async def create_action(
    action_in: ActionCreate,
    session: SessionDep,
    user: Annotated[User, Depends(vt.current_admin_or_manager)],
) -> Action:
    """Создаст новую акцию."""
    return await action_service.create_action(
        action_create=action_in,
        user=user,
        session=session,
    )


@router.get(
    '/{action_id}',
    response_model=ActionInfo,
    responses=er.ERRORS_4XX_FULL,
)
async def get_action(
    action_id: uuid.UUID,
    session: SessionDep,
    user: Annotated[User, Depends(vt.current_user_is_active)],
) -> Action:
    """Вернет акцию по идентификатору."""
    return await action_service.get_action_by_id(
        action_id=action_id,
        session=session,
        user=user,
    )


@router.patch(
    '/{action_id}',
    response_model=ActionInfo,
    responses=er.ERRORS_4XX_FULL,
)
async def update_action(
    action_id: uuid.UUID,
    action_in: ActionUpdate,
    session: SessionDep,
    user: Annotated[User, Depends(vt.current_admin_or_manager)],
) -> Action:
    """Обновит данные существующей акции."""
    return await action_service.update_action(
        action_id=action_id,
        action_update=action_in,
        user=user,
        session=session,
    )
