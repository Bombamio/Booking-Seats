from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import constants as ct
from src.core.db import get_session
from src.models.user import User

ph = PasswordHasher(
    time_cost=ct.HASH_TIME_COST,
    memory_cost=ct.HASH_MEMORY_COST,
    parallelism=ct.HASH_PARALLELISM,
    hash_len=ct.MAX_PASS_HASH_LEN,
    salt_len=ct.HASH_SALT_LEN,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def hash_password(password: str) -> str:
    """Хэширование пароля."""
    return ph.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """Проверка пароля."""
    try:
        ph.verify(hashed, password)
        return True
    except VerifyMismatchError:
        return False


def needs_rehash(hashed: str) -> bool:
    """Проверка необходимости обновления хэша."""
    return ph.check_needs_rehash(hashed)


def create_access_token(
        data: dict,
        expires_delta: timedelta | None = None,
) -> str:
    """Создание JWT токена."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, ct.SECRET_KEY, algorithm=ct.ALGORITHM)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: SessionDep,
) -> User:
    """Получение текущего пользователя."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверные имя пользователя или пароль",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, ct.SECRET_KEY, algorithms=[ct.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    user = await session.get(User, user_id)
    if user is None:
        raise credentials_exception
    return user
