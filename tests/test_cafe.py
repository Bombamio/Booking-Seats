import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import hash_password
from src.crud.cafe import cafe_crud
from src.models import Cafe, User, UserRole
from src.schemas import cafe as schema


@pytest.mark.anyio
async def test_crud_create_cafe(db_session: AsyncSession) -> None:
    """Проверяет создание кафе через CRUD."""
    cafe_in = schema.CafeCreate(
        name='Test Cafe',
        address='Test Address',
        phone='+79991112233',
        description='Test description',
        managers_id=[],
    )

    cafe = await cafe_crud.create_cafe(cafe_in, db_session)

    await db_session.commit()
    await db_session.refresh(cafe)

    assert cafe.id is not None
    assert cafe.name == 'Test Cafe'
    assert cafe.address == 'Test Address'
    assert cafe.phone == '+79991112233'
    assert cafe.description == 'Test description'


@pytest.mark.anyio
async def test_crud_update_cafe(db_session: AsyncSession) -> None:
    """Проверяет обновление данных кафе."""
    cafe = Cafe(
        name='Old Name',
        address='Old Address',
        phone='+79991112233',
        description='Old desc',
    )
    db_session.add(cafe)
    await db_session.commit()
    await db_session.refresh(cafe)

    update_data = schema.CafeUpdate(
        name='New Name',
        address='New Address',
        phone='+79991112244',
        description='New desc',
    )
    updated = await cafe_crud.update_cafe(cafe, update_data, db_session)
    await db_session.commit()
    await db_session.refresh(updated)

    assert updated.name == 'New Name'
    assert updated.address == 'New Address'
    assert updated.phone == '+79991112244'
    assert updated.description == 'New desc'


@pytest.mark.anyio
async def test_crud_get_with_managers(db_session: AsyncSession) -> None:
    """Проверяет получение кафе с менеджерами."""
    cafe = Cafe(name='Test Cafe', address='Test Address', phone='+79991112233')
    db_session.add(cafe)
    await db_session.commit()
    await db_session.refresh(cafe)

    managers = [
        User(
            username=f'manager{i}',
            email=f'manager{i}@example.com',
            phone=None,
            password_hash=hash_password('securepass'),
            role=UserRole.MANAGER,
            cafe_id=cafe.id,
        )
        for i in range(2)
    ]
    db_session.add_all(managers)
    await db_session.commit()

    result = await cafe_crud.get_with_managers(db_session, Cafe.id == cafe.id)
    assert result is not None
    assert result.id == cafe.id
    assert len(result.managers) == 2


@pytest.mark.anyio
async def test_crud_exists(db_session: AsyncSession) -> None:
    """Проверяет метод `exists`."""
    cafe = Cafe(name='Unique', address='Unique', phone='+79991112233')
    db_session.add(cafe)
    await db_session.commit()

    assert await cafe_crud.exists(db_session, Cafe.name == 'Unique') is True
    assert await cafe_crud.exists(db_session, Cafe.name == 'NonExistent') is False
