from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jwt.exceptions import InvalidTokenError

from src.core import constants as ct

ph = PasswordHasher(
    time_cost=ct.HASH_TIME_COST,
    memory_cost=ct.HASH_MEMORY_COST,
    parallelism=ct.HASH_PARALLELISM,
    hash_len=ct.MAX_PASS_HASH_LEN,
    salt_len=ct.HASH_SALT_LEN,
)


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
    encoded_jwt = jwt.encode(
        to_encode, ct.SECRET_KEY, algorithm=ct.ALGORITHM,
    )
    return encoded_jwt
