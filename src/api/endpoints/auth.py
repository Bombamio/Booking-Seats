"""Эндпоинты аутентификации.

Модуль описывает маршруты входа и выдачи JWT-токена.

Маршруты:
   - `POST /login` — получение токена авторизации.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api import error_responses as er
from src.api.openapi_examples import SUCCESS_AUTH_LOGIN, merge_responses
from src.core.db import get_session
from src.schemas import auth as schema
from src.services import AuthService

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.post(
    '/login',
    response_model=schema.AuthToken,
    summary='Получение токена авторизации',
    responses=merge_responses(SUCCESS_AUTH_LOGIN, er.ERRORS_AUTH),
    description='Возвращает токен для последующей авторизации пользователя.',
)
async def login(
    auth_data: schema.AuthData,
    session: SessionDep,
) -> schema.AuthToken:
    """Получение токена авторизации."""
    return await AuthService().authenticate_user(
        session,
        auth_data.login,
        auth_data.password,
    )
