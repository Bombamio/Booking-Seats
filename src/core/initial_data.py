import contextlib

from sqlalchemy import select

from src.core.db import get_session
from src.core.logger import bookingseats_logger
from src.core.security import hash_password
from src.core.settings import settings
from src.models import User
from src.schemas.user import UserRole

get_async_session_context = contextlib.asynccontextmanager(get_session)


async def create_first_users() -> None:
    """Создает админа, менеджера и обычного пользователя, если их нет."""
    if not settings.create_default_users:
        return

    default_users = [
        {
            'username': settings.first_superuser_name,
            'email': settings.first_superuser_email,
            'password': settings.first_superuser_password,
            'role': UserRole.ADMIN,
        },
        {
            'username': settings.first_manager_username,
            'email': settings.first_manager_email,
            'password': settings.first_manager_password,
            'role': UserRole.MANAGER,
        },
        {
            'username': settings.first_user_username,
            'email': settings.first_user_email,
            'password': settings.first_user_password,
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
                password=hash_password(user_data['password']),
                role=user_data['role'],
            )
            session.add(user)
            bookingseats_logger.info(f'Создан пользователь {user_data["username"]} - {user_data["role"]}')
