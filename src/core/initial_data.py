"""Начальные данные приложения.

Модуль описывает создание дефолтных пользователей при старте.

Функции:
   - `create_first_users` — админ, менеджер и пользователь, если их ещё нет.
"""

import contextlib

from sqlalchemy import select

from src.core import constants as ct
from src.core.db import get_session
from src.core.logger import bookingseats_logger
from src.core.security import hash_password
from src.core.settings import settings
from src.models import User, UserRole

get_async_session_context = contextlib.asynccontextmanager(get_session)


async def create_first_users() -> None:
    """Создаст админа, менеджера и обычного пользователя, если их нет."""
    if not settings.create_default_users:
        return

    default_users = [
        {
            'username': ct.FIRST_SUPERUSER_USERNAME,
            'email': ct.FIRST_SUPERUSER_EMAIL,
            'password_hash': ct.FIRST_SUPERUSER_PASSWORD,
            'role': UserRole.ADMIN,
        },
        {
            'username': ct.FIRST_MANAGER_USERNAME,
            'email': ct.FIRST_MANAGER_EMAIL,
            'password_hash': ct.FIRST_MANAGER_PASSWORD,
            'role': UserRole.MANAGER,
        },
        {
            'username': ct.FIRST_USER_USERNAME,
            'email': ct.FIRST_USER_EMAIL,
            'password_hash': ct.FIRST_USER_PASSWORD,
            'role': UserRole.USER,
        },
    ]

    async with get_async_session_context() as session:
        for user_data in default_users:
            stmt = select(User).where(User.email == user_data['email'])
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                bookingseats_logger.debug(f'Пользователь {user_data["email"]} уже существует.')
                continue

            user = User(
                username=user_data['username'],
                email=user_data['email'],
                password_hash=hash_password(user_data['password_hash']),
                role=user_data['role'],
            )
            session.add(user)
            bookingseats_logger.info(f'Создан пользователь {user_data["username"]} - {user_data["role"]}')
