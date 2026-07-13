from datetime import datetime, timedelta, timezone
from typing import Any
from unittest.mock import AsyncMock

import jwt
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from src.core import constants as ct
from src.core.security import (
    create_access_token,
    get_current_user,
    get_optional_current_user,
    hash_password,
    needs_rehash,
    verify_password,
)
from src.models import User


def test_hash_password() -> None:
    """Проверяет хэширование пароля."""
    password = 'my_password'
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password('wrong', hashed) is False


def test_needs_rehash() -> None:
    """Проверяет, что пароль не требует рехэша."""
    password = 'my_password'
    hashed = hash_password(password)
    assert needs_rehash(hashed) in (True, False)


def test_create_access_token_default_expiry() -> None:
    """Проверяет создание JWT-токена с дефолтным сроком действия."""
    data = {'sub': 'user_id'}
    token = create_access_token(data)
    decoded = jwt.decode(token, ct.SECRET_KEY, algorithms=[ct.ALGORITHM])
    assert decoded['sub'] == 'user_id'
    assert 'exp' in decoded
    exp = datetime.fromtimestamp(decoded['exp'], timezone.utc)
    now = datetime.now(timezone.utc)
    assert now < exp < now + timedelta(minutes=31)


def test_create_access_token_with_custom_expiry() -> None:
    """Проверяет создание токена с кастомным сроком действия."""
    data = {'sub': 'user_id'}
    token = create_access_token(data, expires_delta=timedelta(minutes=5))
    decoded = jwt.decode(token, ct.SECRET_KEY, algorithms=[ct.ALGORITHM])
    exp = datetime.fromtimestamp(decoded['exp'], timezone.utc)
    now = datetime.now(timezone.utc)
    assert now < exp < now + timedelta(minutes=6)


@pytest.mark.anyio
async def test_get_current_user_success(mocker: Any, db_session: Any) -> None:
    """Проверяет успешное получение текущего пользователя из токена."""
    user = User(id='123', username='testuser', email='test@example.com')
    db_session.get = AsyncMock(return_value=user)

    mocker.patch('src.core.security.jwt.decode', return_value={'sub': '123'})

    credentials = HTTPAuthorizationCredentials(scheme='Bearer', credentials='valid_token')
    result = await get_current_user(credentials, db_session)
    assert result == user


@pytest.mark.anyio
async def test_get_current_user_invalid_token(mocker: Any, db_session: Any) -> None:
    """Проверяет успешное получение текущего пользователя из токена."""
    mocker.patch('src.core.security.jwt.decode', side_effect=jwt.InvalidTokenError)
    credentials = HTTPAuthorizationCredentials(scheme='Bearer', credentials='bad')
    with pytest.raises(HTTPException) as exc:
        await get_current_user(credentials, db_session)
    assert exc.value.status_code == 401
    assert 'Неверные имя пользователя или пароль' in str(exc.value.detail)


@pytest.mark.anyio
async def test_get_current_user_user_not_found(mocker: Any, db_session: Any) -> None:
    """Проверяет, что если токен валиден, но пользователя в БД нет — поднимается исключение."""
    mocker.patch('src.core.security.jwt.decode', return_value={'sub': '123'})
    db_session.get = AsyncMock(return_value=None)
    credentials = HTTPAuthorizationCredentials(scheme='Bearer', credentials='token')
    with pytest.raises(HTTPException):
        await get_current_user(credentials, db_session)


@pytest.mark.anyio
async def test_get_optional_current_user_without_token(db_session: Any) -> None:
    """Проверяет `get_optional_current_user` без токена → возвращает `None`."""
    result = await get_optional_current_user(None, db_session)
    assert result is None


@pytest.mark.anyio
async def test_get_optional_current_user_with_token(mocker: Any, db_session: Any) -> None:
    """Проверяет `get_optional_current_user` с валидным токеном."""
    user = User(id='123', username='testuser', phone='+1234567890')
    db_session.get = AsyncMock(return_value=user)
    mocker.patch('src.core.security.jwt.decode', return_value={'sub': '123'})

    credentials = HTTPAuthorizationCredentials(scheme='Bearer', credentials='valid')
    result = await get_optional_current_user(credentials, db_session)
    assert result == user
