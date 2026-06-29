from fastapi import APIRouter

from src.schemas import user as schema

router = APIRouter()


@router.post(
    '/login',
    response_model=schema.LoginResponse,
)
async def login():
    """Получение токена авторизации."""
    pass
