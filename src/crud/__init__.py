from .action import CRUDAction, action_crud
from .base import CRUDBase
from .cafe import CRUDCafe, cafe_crud
from .dish import CRUDDish, dish_crud
from .slot import CRUDSlot, slot_crud
from .table import CRUDTable, table_crud

__all__ = [
    'CRUDAction', 'action_crud',
    'CRUDBase',
    'CRUDCafe', 'cafe_crud',
    'CRUDDish', 'dish_crud',
    'CRUDSlot', 'slot_crud',
    'CRUDTable', 'table_crud',
]
