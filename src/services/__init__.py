"""Пакет сервисного слоя проекта BookingSeats.

Модуль реэкспортирует сервисы сущностей и фабрики зависимостей FastAPI.
"""

from src.services.action import ActionService, action_service
from src.services.auth import AuthService
from src.services.base import BaseService
from src.services.booking import BookingService, booking_service
from src.services.cafe import CafeService, get_cafe_service
from src.services.dish import DishService, dish_service
from src.services.media import MediaService, media_service
from src.services.slot import SlotService, get_slot_service
from src.services.table import TableService, table_service
from src.services.user import UserService, user_service

__all__ = [
    'ActionService',
    'AuthService',
    'BaseService',
    'BookingService',
    'CafeService',
    'DishService',
    'MediaService',
    'SlotService',
    'TableService',
    'UserService',
    'action_service',
    'booking_service',
    'dish_service',
    'get_cafe_service',
    'get_slot_service',
    'media_service',
    'table_service',
    'user_service',
]
