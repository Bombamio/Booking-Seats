"""Пакет CRUD-слоя проекта BookingSeats.

Модуль реэкспортирует базовые классы, специализированные CRUD и готовые экземпляры.
"""

from src.crud.action import CRUDAction, action_crud
from src.crud.base import CRUDBase
from src.crud.booking import CRUDBooking, booking_crud
from src.crud.cafe import CRUDCafe, cafe_crud
from src.crud.dish import CRUDDish, dish_crud
from src.crud.slot import CRUDSlot, slot_crud
from src.crud.user import CRUDUser, user_crud
from src.models import Table

table_crud = CRUDBase(Table)

__all__ = [
    'CRUDAction',
    'CRUDBooking',
    'CRUDBase',
    'CRUDCafe',
    'CRUDDish',
    'CRUDSlot',
    'CRUDUser',
    'action_crud',
    'booking_crud',
    'cafe_crud',
    'dish_crud',
    'slot_crud',
    'table_crud',
    'user_crud',
]
