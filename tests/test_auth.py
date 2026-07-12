from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User
from src.services.auth import AuthService


@pytest.mark.asyncio
async def test_auth_service_authenticate_user_not_found(mocker: AsyncMock, db_session: AsyncSession) -> None:
    """Проверяет, что при попытке аутентификации несуществующего пользователя возвращается None."""
    mocker.patch('src.crud.user.user_crud.get', AsyncMock(return_value=None))

    service = AuthService()
    with pytest.raises(Exception) as exc:
        await service.authenticate_user(
            session=db_session,
            login='nonexistent@example.com',
            password='pass',
        )
    assert 'Неверные имя пользователя или пароль' in str(exc.value)


@pytest.mark.asyncio
async def test_auth_service_authenticate_user_wrong_password(
    mocker: AsyncMock,
    db_session: AsyncSession,
) -> None:
    """Проверяет, что при неправильном пароле аутентификация возвращает None."""
    mock_user = User(id='123', email='user@example.com', password_hash='hashed')
    mocker.patch('src.crud.user.user_crud.get', AsyncMock(return_value=mock_user))
    mocker.patch('src.core.security.verify_password', return_value=False)

    service = AuthService()
    with pytest.raises(Exception):
        await service.authenticate_user(
            session=db_session,
            login='user@example.com',
            password='wrong',
        )
