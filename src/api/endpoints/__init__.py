from .cafe import router as cafe_router
from .dish import router as dish_router
from .slot import router as slot_router

__all__ = [
    'dish_router',
    'slot_router',
    'cafe_router',
]
