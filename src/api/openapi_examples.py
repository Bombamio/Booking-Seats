"""Примеры успешных ответов API для документации OpenAPI.

Модуль собирает примеры из Pydantic-схем, чтобы они совпадали с ``response_model``.
"""

from datetime import date, datetime, time
from uuid import UUID

from fastapi import status

from src.models import BookingStatus, UserRole
from src.schemas import (
    ActionInfo,
    AuthToken,
    BookingDishInfo,
    BookingInfo,
    BookingTableSlotShortInfo,
    CafeInfo,
    CafeShortInfo,
    DishInfo,
    MediaInfo,
    TableInfo,
    TableShortInfo,
    TimeSlotInfo,
    TimeSlotShortInfo,
    UserInfo,
    UserShortInfo,
)

CAFE_ID = UUID('11111111-1111-4111-8111-111111111111')
USER_ID = UUID('22222222-2222-4222-8222-222222222222')
MANAGER_ID = UUID('33333333-3333-4333-8333-333333333333')
TABLE_ID = UUID('44444444-4444-4444-8444-444444444444')
SLOT_ID = UUID('55555555-5555-4555-8555-555555555555')
DISH_ID = UUID('66666666-6666-4666-8666-666666666666')
ACTION_ID = UUID('77777777-7777-4777-8777-777777777777')
BOOKING_ID = UUID('88888888-8888-4888-8888-888888888888')
MEDIA_ID = UUID('99999999-9999-4999-8999-999999999999')
PHOTO_ID = UUID('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa')

CREATED_AT = datetime(2026, 7, 1, 10, 0, 0)
UPDATED_AT = datetime(2026, 7, 12, 12, 0, 0)
BOOKING_DATE = date(2026, 7, 20)


def _json(model: object) -> dict | list:
    """Сериализует Pydantic-модель в JSON-совместимый словарь."""
    return model.model_dump(mode='json')


def success_json(
    example: dict | list,
    *,
    status_code: int = status.HTTP_200_OK,
    description: str = 'Успешный ответ',
) -> dict:
    """Соберёт блок ``responses`` OpenAPI для успешного JSON-ответа."""
    return {
        status_code: {
            'description': description,
            'content': {
                'application/json': {
                    'example': example,
                },
            },
        },
    }


def merge_responses(*parts: dict) -> dict:
    """Объединит успешные и ошибочные ответы для параметра ``responses``."""
    merged: dict = {}
    for part in parts:
        merged.update(part)
    return merged


EXAMPLE_USER_SHORT = UserShortInfo(
    id=USER_ID,
    username='demo_user',
    email='user@demo.local',
    phone='+79991234567',
    tg_id=None,
    is_active=True,
)

EXAMPLE_MANAGER_SHORT = UserShortInfo(
    id=MANAGER_ID,
    username='demo_manager',
    email='manager@demo.local',
    phone='+79997654321',
    tg_id=None,
    is_active=True,
)

EXAMPLE_CAFE_SHORT = CafeShortInfo(
    id=CAFE_ID,
    name='Демо Кафе',
    address='ул. Примерная, 1',
    phone='+74951234567',
    description='Уютное кафе для демонстрации API',
    is_active=True,
    photo_id=PHOTO_ID,
)

EXAMPLE_USER_INFO = _json(
    UserInfo(
        id=USER_ID,
        username='demo_user',
        email='user@demo.local',
        phone='+79991234567',
        tg_id=None,
        is_active=True,
        role=UserRole.USER,
        cafe_id=None,
        created_at=CREATED_AT,
        updated_at=UPDATED_AT,
    ),
)

EXAMPLE_CAFE_INFO = _json(
    CafeInfo(
        id=CAFE_ID,
        name='Демо Кафе',
        address='ул. Примерная, 1',
        phone='+74951234567',
        description='Уютное кафе для демонстрации API',
        is_active=True,
        photo_id=PHOTO_ID,
        managers=[EXAMPLE_MANAGER_SHORT],
        created_at=CREATED_AT,
        updated_at=UPDATED_AT,
    ),
)

EXAMPLE_DISH_INFO = _json(
    DishInfo(
        id=DISH_ID,
        name='Капучино',
        price=350,
        description='Классический капучино 250 мл',
        is_active=True,
        photo_id=PHOTO_ID,
        cafes=[EXAMPLE_CAFE_SHORT],
        created_at=CREATED_AT,
        updated_at=UPDATED_AT,
    ),
)

EXAMPLE_ACTION_INFO = _json(
    ActionInfo(
        id=ACTION_ID,
        description='Скидка 10% на завтраки по будням',
        is_active=True,
        photo_id=PHOTO_ID,
        cafes=[EXAMPLE_CAFE_SHORT],
        created_at=CREATED_AT,
        updated_at=UPDATED_AT,
    ),
)

EXAMPLE_TABLE_INFO = _json(
    TableInfo(
        id=TABLE_ID,
        seat_number=4,
        description='Стол у окна',
        is_active=True,
        cafe=EXAMPLE_CAFE_SHORT,
        created_at=CREATED_AT,
        updated_at=UPDATED_AT,
    ),
)

EXAMPLE_SLOT_INFO = _json(
    TimeSlotInfo(
        id=SLOT_ID,
        start_time=time(12, 0),
        end_time=time(14, 0),
        description='Обеденный слот',
        is_active=True,
        cafe=EXAMPLE_CAFE_SHORT,
        created_at=CREATED_AT,
        updated_at=UPDATED_AT,
    ),
)

EXAMPLE_BOOKING_INFO = _json(
    BookingInfo(
        id=BOOKING_ID,
        user=EXAMPLE_USER_SHORT,
        cafe=EXAMPLE_CAFE_SHORT,
        tables_slots=[
            BookingTableSlotShortInfo(
                table=TableShortInfo(
                    id=TABLE_ID,
                    seat_number=4,
                    description='Стол у окна',
                    is_active=True,
                ),
                slot=TimeSlotShortInfo(
                    id=SLOT_ID,
                    start_time=time(12, 0),
                    end_time=time(14, 0),
                    description='Обеденный слот',
                    is_active=True,
                ),
            ),
        ],
        preordered_dishes=[
            BookingDishInfo(
                dish=DishInfo(
                    id=DISH_ID,
                    name='Капучино',
                    price=350,
                    description='Классический капучино 250 мл',
                    is_active=True,
                    photo_id=PHOTO_ID,
                    cafes=[EXAMPLE_CAFE_SHORT],
                    created_at=CREATED_AT,
                    updated_at=UPDATED_AT,
                ),
                quantity=2,
            ),
        ],
        guest_number=2,
        note='Стол у окна, если возможно',
        status=BookingStatus.BOOKING,
        booking_date=BOOKING_DATE,
        is_active=True,
        created_at=CREATED_AT,
        updated_at=UPDATED_AT,
    ),
)

EXAMPLE_AUTH_TOKEN = _json(
    AuthToken(
        access_token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.example',
        token_type='Bearer',
    ),
)

EXAMPLE_MEDIA_INFO = _json(MediaInfo(media_id=MEDIA_ID))

EXAMPLE_HEALTH_OK = {'status': 'ok'}

EXAMPLE_HEALTH_READY = {
    'status': 'ready',
    'checks': {
        'database': 'ok',
        'redis': 'ok',
    },
}

EXAMPLE_INDEX = {
    'app': 'BookingSeats (1.0.0)',
    'description': 'API сервиса бронирования столиков в кафе',
    'status': 'OK',
}

SUCCESS_AUTH_LOGIN = success_json(EXAMPLE_AUTH_TOKEN)
SUCCESS_USER_INFO = success_json(EXAMPLE_USER_INFO)
SUCCESS_USERS_LIST = success_json([EXAMPLE_USER_INFO])
SUCCESS_CAFE_INFO = success_json(EXAMPLE_CAFE_INFO)
SUCCESS_CAFES_LIST = success_json([EXAMPLE_CAFE_INFO])
SUCCESS_DISH_INFO = success_json(EXAMPLE_DISH_INFO)
SUCCESS_DISHES_LIST = success_json([EXAMPLE_DISH_INFO])
SUCCESS_ACTION_INFO = success_json(EXAMPLE_ACTION_INFO)
SUCCESS_ACTIONS_LIST = success_json([EXAMPLE_ACTION_INFO])
SUCCESS_TABLE_INFO = success_json(EXAMPLE_TABLE_INFO)
SUCCESS_TABLES_LIST = success_json([EXAMPLE_TABLE_INFO])
SUCCESS_SLOT_INFO = success_json(EXAMPLE_SLOT_INFO)
SUCCESS_SLOTS_LIST = success_json([EXAMPLE_SLOT_INFO])
SUCCESS_BOOKING_INFO = success_json(EXAMPLE_BOOKING_INFO)
SUCCESS_BOOKINGS_LIST = success_json([EXAMPLE_BOOKING_INFO])
SUCCESS_MEDIA_INFO = success_json(EXAMPLE_MEDIA_INFO, status_code=status.HTTP_201_CREATED)
SUCCESS_HEALTH_OK = success_json(EXAMPLE_HEALTH_OK)
SUCCESS_HEALTH_READY = success_json(EXAMPLE_HEALTH_READY)
SUCCESS_INDEX = success_json(EXAMPLE_INDEX, description='Информация о приложении')

SUCCESS_USER_CREATED = success_json(
    EXAMPLE_USER_INFO,
    status_code=status.HTTP_201_CREATED,
    description='Пользователь создан',
)
SUCCESS_CAFE_CREATED = success_json(
    EXAMPLE_CAFE_INFO,
    status_code=status.HTTP_201_CREATED,
    description='Кафе создано',
)
SUCCESS_DISH_CREATED = success_json(
    EXAMPLE_DISH_INFO,
    status_code=status.HTTP_201_CREATED,
    description='Блюдо создано',
)
SUCCESS_ACTION_CREATED = success_json(
    EXAMPLE_ACTION_INFO,
    status_code=status.HTTP_201_CREATED,
    description='Акция создана',
)
SUCCESS_TABLE_CREATED = success_json(
    EXAMPLE_TABLE_INFO,
    status_code=status.HTTP_201_CREATED,
    description='Стол создан',
)
SUCCESS_SLOT_CREATED = success_json(
    EXAMPLE_SLOT_INFO,
    status_code=status.HTTP_201_CREATED,
    description='Слот создан',
)
SUCCESS_BOOKING_CREATED = success_json(
    EXAMPLE_BOOKING_INFO,
    status_code=status.HTTP_201_CREATED,
    description='Бронирование создано',
)

EXAMPLE_JPEG_BASE64 = (
    '/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRof'
    'Hh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwh'
    'MjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAAB'
    'AAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAn/xAAUEAEAAAAAAAAAAAAAAAAAAAAA'
    '/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEA'
    'PwCwAA//2Q=='
)

SUCCESS_MEDIA_IMAGE = {
    status.HTTP_200_OK: {
        'description': 'Изображение в формате JPEG',
        'content': {
            'image/jpeg': {
                'example': EXAMPLE_JPEG_BASE64,
            },
        },
    },
}
