from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_session
from src.schemas import user as schema

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get(
    '/',
    response_model=list[schema.UserInfo],
)
async def get_users_list():
    """Получение списка пользователей.

    Только для администраторов или менеджеров.
    """


@router.get(
    '/{user_id}',
    response_model=schema.UserInfo,
)
async def get_user(user_id: str):
    """Получение информации о пользователе по его ID.

    Только для администраторов или менеджеров.
    """


@router.post(
    '/',
    response_model=schema.UserInfo,
)
async def create_user():
    """Создание нового пользователя."""


@router.put(
    '/{user_id}',
    response_model=schema.UserInfo,
)
async def update_user(user_id: str):
    """Обновление информации о пользователе по его ID.

    Только для администраторов или менеджеров
    """


@router.get(
    '/me',
    response_model=schema.UserInfo,
)
async def get_me():
    """Получение информации о текущем пользователе."""


@router.put(
    '/me',
    response_model=schema.UserInfo,
)
async def update_me():
    """Обновление информации о текущем пользователе."""
