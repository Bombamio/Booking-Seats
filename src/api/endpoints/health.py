"""Эндпоинты для проверки работоспособности сервиса."""

from fastapi import APIRouter
from sqlalchemy import text

from src.core.cache import cache
from src.core.db import async_engine

router = APIRouter(prefix='/health', tags=['Health'])


@router.get('/')
async def liveness() -> dict:
    """Быстрая проверка: Ответ сервиса."""
    return {'status': 'ok'}


@router.get('/ready')
async def readiness() -> dict:
    """Полная проверка: Работа зависимостей."""
    checks = {}

    try:
        async with async_engine.connect() as conn:
            await conn.execute(text('SELECT 1'))
        checks['database'] = 'ok'
    except Exception as e:
        checks['database'] = f'error: {str(e)}'

    try:
        if cache.redis:
            await cache.redis.ping()
        checks['redis'] = 'ok'
    except Exception as e:
        checks['redis'] = f'error: {str(e)}'

    all_ok = all(v == 'ok' for v in checks.values())

    return {
        'status': 'ready' if all_ok else 'not ready',
        'checks': checks,
    }
