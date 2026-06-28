from .dish import router as dish_router
from .media import router as media_router
from .slot import router as slot_router
from .table import router as table_router

__all__ = [
    'dish_router',
    'media_router',
    'slot_router',
    'table_router',
]
