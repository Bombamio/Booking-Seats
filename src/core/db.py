"""Подключение к базе данных и сессии SQLAlchemy.

Модуль описывает async engine, session maker и зависимость FastAPI ``get_session``.

Функции:
   - `get_session` — сессия с commit, rollback и обработкой ошибок БД.
"""

from typing import AsyncIterator

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.core.logger import bookingseats_logger
from src.core.settings import settings

async_engine = create_async_engine(
    url=settings.db_url,
    pool_pre_ping=True,
)

session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Вернёт асинхронную сессию для FastAPI Depends."""
    async with session_maker() as session:
        try:
            yield session  # noqa: ASYNC119
            await session.commit()
        except IntegrityError as exc:
            await session.rollback()
            bookingseats_logger.warning(exc)
            detail = 'Нарушение уникальности данных'
            err = str(exc).lower()
            if 'users_phone' in err or 'users_email' in err or 'phone' in err or 'email' in err:
                detail = 'Пользователь с таким email/phone уже существует'
            raise HTTPException(
                status_code=422,
                detail=detail,
            )
        except SQLAlchemyError as exc:
            await session.rollback()
            bookingseats_logger.error(exc)
            raise HTTPException(
                status_code=500,
                detail='Ошибка при работе с БД',
            )
        finally:
            await session.close()
