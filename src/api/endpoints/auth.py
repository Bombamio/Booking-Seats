from fastapi import APIRouter

from src.schemas import auth as schema

router = APIRouter()


@router.post(
    '/login',
    response_model=schema.AuthToken,
)
async def login():
    """Получение токена авторизации."""
    pass
