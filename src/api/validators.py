"""Зависимости FastAPI для проверки прав доступа.

Модуль описывает валидаторы авторизации и ролей пользователя.

Функции:
   - `current_user_is_active` — активный авторизованный пользователь;
   - `current_admin` — только администратор;
   - `current_admin_or_manager` — администратор или менеджер.
"""

from http import HTTPStatus

from fastapi import Depends, HTTPException

from src.core.security import get_current_user
from src.models import User, UserRole


async def current_user_is_active(
    user: User = Depends(get_current_user),
) -> User:
    """Валидатор проверки **авторизации** пользователя."""
    if not user.is_active:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Неавторизированный пользователь',
        )
    return user


async def current_admin(
    user: User = Depends(current_user_is_active),
) -> User:
    """Валидатор проверки прав **администратора**."""
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Доступ запрещен',
        )
    return user


async def current_admin_or_manager(
    user: User = Depends(current_user_is_active),
) -> User:
    """Валидатор проверки прав **админа** или **менеджера**."""
    if user.role not in (UserRole.ADMIN, UserRole.MANAGER):
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Доступ запрещен',
        )
    return user
