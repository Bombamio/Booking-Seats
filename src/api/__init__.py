from src.api.endpoints.actions import router as action_router
from src.api.endpoints.auth import router as auth_router
from src.api.endpoints.cafe import router as cafe_router
from src.api.endpoints.dish import router as dish_router
from src.api.endpoints.health import router as health_router
from src.api.endpoints.media import router as media_router
from src.api.endpoints.slot import router as slot_router
from src.api.endpoints.table import router as table_router
from src.api.endpoints.user import router as user_router

__all__ = [
    'action_router',
    'auth_router',
    'cafe_router',
    'dish_router',
    'health_router',
    'media_router',
    'slot_router',
    'table_router',
    'user_router',
]
