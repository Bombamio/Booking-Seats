from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI

from core.cache import cache
from core.error_handlers import register_error_handlers
from core.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Жизненный цикл приложения FastAPI."""
    # TODO: Добавить код, выполняемый при старте приложения
    await cache.connect()
    yield
    # TODO: Добавить код, выполняемый при остановке приложения
    if cache.redis:
        await cache.redis.close()


app = FastAPI(
    title=settings.title,
    version=settings.version,
    description=settings.description,
)

register_error_handlers(app)


@app.get(
    path='/',
    response_model=dict,
)
async def index() -> dict:
    """Основная страница."""
    return {
        'app': f'{settings.title} ({settings.version})',
        'description': settings.description,
        'status': 'OK',
    }


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
