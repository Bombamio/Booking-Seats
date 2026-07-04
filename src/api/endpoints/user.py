from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

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
    description=('Возвращает информацию о всех пользователях.Только для администраторов или менеджеров'),
)
async def get_users_list(
    session: SessionDep,
    current_user: User = Depends(get_current_user),
) -> list[schema.UserInfo]:
    """Получение списка пользователей.

    Только для администраторов или менеджеров.
    """
    return await user_service.get_users_list(session, current_user)


@router.get(
    '/{user_id}',
    response_model=schema.UserInfo,
)
async def get_user(
    session: SessionDep,
    user_id: str,
    current_user: User = Depends(get_current_user),
) -> schema.UserInfo:
    """Получение информации о пользователе по его ID.

    Только для администраторов или менеджеров.
    """
    return await user_service.get_user(session=session, user_id=user_id, current_user=current_user)


@router.post(
    '/',
    response_model=schema.UserInfo,
)
async def create_user(
    user_in: schema.UserCreate,
    session: SessionDep,
) -> schema.UserInfo:
    """Создание нового пользователя."""
    return await user_service.create_user(
        session=session,
        user_in=user_in,
    )


@router.put(
    '/{user_id}',
    response_model=schema.UserInfo,
)
async def update_user(
    session: SessionDep,
    user_id: str,
    current_user: User = Depends(get_current_user),
) -> schema.UserInfo:
    """Обновление информации о пользователе по его ID.

    Только для администраторов или менеджеров
    """
    return await user_service.update_user(session, user_id, current_user)


@router.get(
    '/me',
    response_model=schema.UserInfo,
)
async def get_me(
    session: SessionDep,
    current_user: User = Depends(get_current_user),
) -> schema.UserInfo:
    """Получение информации о текущем пользователе."""
    return await user_service.get_me(session, current_user)


@router.put(
    '/me',
    response_model=schema.UserInfo,
)
async def update_me(
    session: SessionDep,
    current_user: User = Depends(get_current_user),
) -> schema.UserInfo:
    """Обновление информации о текущем пользователе."""
    return await user_service.update_me(session, current_user)
