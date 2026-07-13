import uuid
from typing import Any

import pytest
from sqlalchemy.exc import IntegrityError

from src.core.security import hash_password, verify_password
from src.crud.user import user_crud
from src.models.user import User, UserRole
from src.schemas import user as schema


@pytest.mark.asyncio
async def test_validate_cafe_id_user_with_cafe_raises(db_session: Any) -> None:
    """Проверяет, что обычный пользователь (USER) не может иметь кафе."""
    user = User(
        username='user',
        email='user@example.com',
        phone=None,
        password_hash=hash_password('securepass'),
        role=UserRole.USER,
        cafe_id=uuid.uuid4(),
    )
    db_session.add(user)

    with pytest.raises(IntegrityError):
        await db_session.commit()


@pytest.mark.asyncio
async def test_validate_cafe_id_admin_with_cafe_raises(db_session: Any) -> None:
    """Проверяет, что администратор (ADMIN) не может иметь кафе."""
    user = User(
        username='admin',
        email='admin@example.com',
        phone=None,
        password_hash=hash_password('securepass'),
        role=UserRole.ADMIN,
        cafe_id=uuid.uuid4(),
    )
    db_session.add(user)

    with pytest.raises(IntegrityError):
        await db_session.commit()


@pytest.mark.asyncio
async def test_crud_create_user(db_session: Any) -> None:
    """Проверяет создание пользователя через CRUD."""
    user_in = schema.UserCreate(
        username='testuser',
        email='test@example.com',
        phone=None,
        password='securepassword',
    )
    user = await user_crud.create(user_in, db_session)
    assert user.id is not None
    assert user.username == 'testuser'
    assert user.email == 'test@example.com'
    assert user.phone is None
    assert verify_password('securepassword', user.password_hash) is True
    assert user.role == UserRole.USER
    assert user.is_active is True


@pytest.mark.asyncio
async def test_crud_duplicate_contact_email(db_session: Any) -> None:
    """Проверяет обнаружение дубликата email."""
    user_in1 = schema.UserCreate(
        username='user1',
        email='dup@example.com',
        phone=None,
        password='securepass1',
    )
    await user_crud.create(user_in1, db_session)

    assert (
        await user_crud.duplicate_contact(
            db_session,
            email='dup@example.com',
            phone=None,
        )
        is True
    )

    assert (
        await user_crud.duplicate_contact(
            db_session,
            email=None,
            phone='+79991112233',
        )
        is False
    )


@pytest.mark.asyncio
async def test_crud_duplicate_contact_phone(db_session: Any) -> None:
    """Проверяет обнаружение дубликата телефона."""
    user_in1 = schema.UserCreate(
        username='user1',
        email=None,
        phone='+79991112233',
        password='securepass2',
    )
    await user_crud.create(user_in1, db_session)

    assert (
        await user_crud.duplicate_contact(
            db_session,
            email=None,
            phone='+79991112233',
        )
        is True
    )


@pytest.mark.asyncio
async def test_crud_duplicate_contact_exclude_id(db_session: Any) -> None:
    """Проверяет, что при обновлении пользователя дубликат самого себя не считается."""
    user_in = schema.UserCreate(
        username='user1',
        email='dup@example.com',
        phone=None,
        password='securepass3',
    )
    user = await user_crud.create(user_in, db_session)

    assert (
        await user_crud.duplicate_contact(
            db_session,
            email='dup@example.com',
            phone=None,
            exclude_id=user.id,
        )
        is False
    )


@pytest.mark.asyncio
async def test_crud_update_user(db_session: Any) -> None:
    """Проверяет обновление данных пользователя."""
    user_in = schema.UserCreate(
        username='oldname',
        email='old@example.com',
        phone=None,
        password='oldpassword',
    )
    user = await user_crud.create(user_in, db_session)

    update_data = schema.UserUpdate(
        username='newname',
        email='new@example.com',
        password='newpassword',
    )
    updated = await user_crud.update(user, update_data, db_session)

    assert updated.username == 'newname'
    assert updated.email == 'new@example.com'
    assert verify_password('newpassword', updated.password_hash) is True
