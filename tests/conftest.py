import asyncio
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.core.base_model import Base
from src.core.db import get_session
from src.main import app

TEST_DATABASE_URL = 'sqlite+aiosqlite:///./test.db'

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
    """Переопределяет зависимость `get_session` для тестов."""
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_session] = override_get_session


@pytest.fixture(scope='session')
def event_loop() -> asyncio.AbstractEventLoop:
    """Создаёт event loop для асинхронных тестов."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='function', autouse=True)
async def setup_db() -> None:
    """Создаёт таблицы перед каждым тестом и очищает после."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope='function')
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Возвращает асинхронную тестовую сессию SQLAlchemy."""
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope='function')
def client() -> Generator:
    """Создаёт синхронный тестовый клиент FastAPI (`TestClient`)."""
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope='function')
async def async_client() -> AsyncGenerator:
    """Создаёт асинхронный тестовый клиент (`httpx.AsyncClient`)."""
    async with AsyncClient(app=app, base_url='http://test') as ac:
        yield ac
