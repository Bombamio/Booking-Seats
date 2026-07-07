from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api import error_responses as er
from src.core.db import get_session
from src.schemas import auth as schema
from src.services import AuthService

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.post(
    '/login',
    response_model=schema.AuthToken,
    summary='Получение токена авторизации',
    responses=er.ERRORS_AUTH,
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
