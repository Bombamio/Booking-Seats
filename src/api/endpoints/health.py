"""Эндпоинты для проверки работоспособности сервиса."""

from fastapi import APIRouter
from redis.exceptions import RedisError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from src.api.openapi_examples import SUCCESS_HEALTH_OK, SUCCESS_HEALTH_READY
from src.core.cache import cache
from src.core.db import async_engine

router = APIRouter(prefix='/health', tags=['Health'])


@router.get('/', responses=SUCCESS_HEALTH_OK)
async def liveness() -> dict:
    """Быстрая проверка: ответ сервиса без обращения к зависимостям."""
    return {'status': 'ok'}


@router.get('/ready', responses=SUCCESS_HEALTH_READY)
async def readiness() -> dict:
    """Полная проверка: доступность PostgreSQL и Redis."""
    checks = {}

    try:
        async with async_engine.connect() as conn:
            await conn.execute(text('SELECT 1'))
        checks['database'] = 'ok'
    except SQLAlchemyError as exc:
        checks['database'] = f'error: {exc}'

    try:
        if cache.redis:
            await cache.redis.ping()
        checks['redis'] = 'ok'
    except (RedisError, OSError) as exc:
        checks['redis'] = f'error: {exc}'

    all_ok = all(value == 'ok' for value in checks.values())

    return {
        'status': 'ready' if all_ok else 'not ready',
        'checks': checks,
    }
