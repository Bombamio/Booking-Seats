from .cafe import router as cafe_router
from .dish import router as dish_router
from .media import router as media_router
from .slot import router as slot_router
from .table import router as table_router
from .user import router as user_router

__all__ = [
    'dish_router',
    'media_router',
    'slot_router',
    'table_router',
    'cafe_router',
    'user_router',
]
