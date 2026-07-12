"""Безопасность и аутентификация.

Модуль описывает хеширование паролей, JWT-токены и зависимости текущего пользователя.

Функции:
   - `hash_password`, `verify_password`, `needs_rehash` — Argon2;
   - `create_access_token` — выпуск JWT;
   - `get_current_user`, `get_optional_current_user` — FastAPI Depends.
"""

from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import constants as ct
from src.core.db import get_session
from src.core.logger import current_user_var
from src.models import User

ph = PasswordHasher(
    time_cost=ct.HASH_TIME_COST,
    memory_cost=ct.HASH_MEMORY_COST,
    parallelism=ct.HASH_PARALLELISM,
    salt_len=ct.HASH_SALT_LEN,
)

security = HTTPBearer()
security_optional = HTTPBearer(auto_error=False)

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def hash_password(password: str) -> str:
    """Захеширует пароль с помощью Argon2."""
    return ph.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """Проверит соответствие пароля хешу."""
    try:
        ph.verify(hashed, password)
        return True
    except VerifyMismatchError:
        return False


def needs_rehash(hashed: str) -> bool:
    """Проверит, нужно ли обновить параметры хеша пароля."""
    return ph.check_needs_rehash(hashed)


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
) -> str:
    """Создаст JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ct.ACCESS_TOKEN_EXPIRE_MINUTES,
        )
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, ct.SECRET_KEY, algorithm=ct.ALGORITHM)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: SessionDep,
) -> User:
    """Вернёт текущего пользователя и запишет его в контекст логгера."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Неверные имя пользователя или пароль',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    token = credentials.credentials
    try:
        payload = jwt.decode(token, ct.SECRET_KEY, algorithms=[ct.ALGORITHM])
        user_id = payload.get('sub')
        if user_id is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    user = await session.get(User, user_id)
    if user is None:
        raise credentials_exception
    current_user_var.set(f'{user.username}({user.id})')
    return user


async def get_optional_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(security_optional),
    ],
    session: SessionDep,
) -> User | None:
    """Вернёт текущего пользователя или ``None`` для неавторизованных запросов."""
    if credentials is None:
        return None
    return await get_current_user(credentials, session)
