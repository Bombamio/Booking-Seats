import uuid
from unittest.mock import AsyncMock, patch

import pytest

from src.core.exceptions import BookingSeatsAppError
from src.models import Cafe, User, UserRole
from src.schemas import cafe as schema
from src.services.cafe import CafeService


@pytest.fixture
def mock_session() -> AsyncMock:
    """Возвращает асинхронную сессию для мокинга."""
    return AsyncMock()


@pytest.fixture
def cafe_service(mock_session: AsyncMock) -> CafeService:
    """Создаёт сервис кафе с mock сессией."""
    return CafeService(mock_session)


@pytest.mark.asyncio
async def test_create_cafe_success(
    cafe_service: CafeService,
    mock_session: AsyncMock,
) -> None:
    """Проверяет успешное создание кафе в сервисе."""
    cafe_in = schema.CafeCreate(
        name='New Cafe',
        address='New Address',
        phone='+79991112233',
        managers_id=[uuid.uuid4()],
    )
    cafe_service._validate_unique_cafe_and_address = AsyncMock(return_value=None)
    manager = User(id=uuid.uuid4(), username='manager', email='manager@example.com', role=UserRole.MANAGER)
    cafe_service._validate_managers = AsyncMock(return_value=[manager])
    new_cafe = Cafe(id=uuid.uuid4(), name='New Cafe', address='New Address', phone='+79991112233')
    with patch('src.services.cafe.cafe_crud.create_cafe', new=AsyncMock(return_value=new_cafe)):
        with patch('src.services.cafe.user_crud.update_link_in_cafe', new=AsyncMock()) as mock_update:
            result = await cafe_service.create_cafe(cafe_in)
            mock_update.assert_awaited_once()
            mock_session.commit.assert_awaited_once()
            mock_session.refresh.assert_awaited_once()
            assert result == new_cafe


@pytest.mark.asyncio
async def test_create_cafe_duplicate_name_address(cafe_service: CafeService) -> None:
    """Проверяет, что создание дубликата (по name+address) вызывает исключение."""
    cafe_in = schema.CafeCreate(
        name='Duplicate',
        address='Duplicate',
        phone='+79991112233',
        managers_id=[],
    )
    cafe_service._validate_unique_cafe_and_address = AsyncMock(
        side_effect=BookingSeatsAppError(422, 'Exists'),
    )
    with pytest.raises(BookingSeatsAppError):
        await cafe_service.create_cafe(cafe_in)


@pytest.mark.asyncio
async def test_get_cafe_not_found(cafe_service: CafeService) -> None:
    """Проверяет поведение при несуществующем кафе."""
    cafe_id = uuid.uuid4()
    user = User(role=UserRole.ADMIN, email='admin@example.com')
    with patch('src.services.cafe.cafe_crud.get_with_managers', new=AsyncMock(return_value=None)):
        with pytest.raises(BookingSeatsAppError) as exc:
            await cafe_service.get_cafe(cafe_id, user)
        assert exc.value.code == 404


@pytest.mark.asyncio
async def test_validate_unique_cafe_and_address_existing(cafe_service: CafeService) -> None:
    """Проверяет валидацию уникальности кафе при создании."""
    name = 'Test'
    address = 'Test'
    is_active = True
    with patch('src.services.cafe.cafe_crud.exists', new=AsyncMock(return_value=True)):
        with pytest.raises(BookingSeatsAppError) as exc:
            await cafe_service._validate_unique_cafe_and_address(name, address, is_active)
        assert exc.value.code == 422
        assert 'уже существует кафе' in exc.value.message
