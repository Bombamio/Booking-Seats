from src.crud.action import CRUDAction, action_crud
from src.crud.base import CRUDBase
from src.crud.booking import CRUDBooking, booking_crud
from src.crud.cafe import CRUDCafe, cafe_crud
from src.crud.dish import CRUDDish, dish_crud
from src.crud.slot import CRUDSlot, slot_crud
from src.crud.table import CRUDTable, table_crud
from src.crud.user import CRUDUser, user_crud

__all__ = [
    'CRUDAction',
    'CRUDBooking',
    'CRUDBase',
    'CRUDCafe',
    'CRUDDish',
    'CRUDSlot',
    'CRUDTable',
    'CRUDUser',
    'action_crud',
    'booking_crud',
    'cafe_crud',
    'dish_crud',
    'slot_crud',
    'table_crud',
    'user_crud',
]
