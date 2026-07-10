from typing import Annotated, Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api import error_responses as er
from src.core.db import get_session
from src.core.security import get_current_user
from src.models import User
from src.schemas import user as schema
from src.services import user_service

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get(
    '/',
    response_model=list[schema.UserInfo],
    summary='Получение списка пользователей',
    responses=er.ERRORS_GET_MULTI_USERS,
    description=('Возвращает информацию о всех пользователях.Только для администраторов или менеджеров'),
)
async def get_users_list(
    session: SessionDep,
    current_user: User = Depends(get_current_user),
) -> Sequence[User]:
    """Получение списка пользователей.

    Только для администраторов или менеджеров.
    """
    return await user_service.get_users_list(session, current_user)


@router.get(
    '/me',
    response_model=schema.UserInfo,
    responses=er.ERRORS_GET_ME,
)
async def get_me(
    session: SessionDep,
    current_user: User = Depends(get_current_user),
) -> User:
    """Получение информации о текущем пользователе."""
    return await user_service.get_me(session, current_user)


@router.patch(
    '/me',
    response_model=schema.UserInfo,
    responses=er.ERRORS_UPDATE_ME,
)
async def update_me(
    session: SessionDep,
    user_in: schema.UserUpdate,
    current_user: User = Depends(get_current_user),
) -> User:
    """Обновление информации о текущем пользователе."""
    return await user_service.update_me(session, user_in, current_user)


@router.get(
    '/{user_id}',
    response_model=schema.UserInfo,
    responses=er.ERRORS_GET_USERS,
)
async def get_user(
    session: SessionDep,
    user_id: UUID,
    current_user: User = Depends(get_current_user),
) -> User:
    """Получение информации о пользователе по его ID.

    Только для администраторов или менеджеров.
    """
    return await user_service.get_user(session=session, user_id=user_id, current_user=current_user)


@router.post(
    '/',
    response_model=schema.UserInfo,
    status_code=status.HTTP_201_CREATED,
    responses=er.ERRORS_POST_USERS,
)
async def create_user(
    user_in: schema.UserCreate,
    session: SessionDep,
) -> User:
    """Создание нового пользователя."""
    return await user_service.create_user(
        session=session,
        user_in=user_in,
    )


@router.patch(
    '/{user_id}',
    response_model=schema.UserInfo,
    responses=er.ERRORS_4XX_FULL,
)
async def update_user(
    session: SessionDep,
    user_id: UUID,
    user_in: schema.UserUpdate,
    current_user: User = Depends(get_current_user),
) -> User:
    """Обновление информации о пользователе по его ID.

    Только для администраторов или менеджеров
    """
    return await user_service.update_user(session, user_id, user_in, current_user)
