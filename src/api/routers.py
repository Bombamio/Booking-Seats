from fastapi import APIRouter

from src.api import endpoints

main_router = APIRouter(prefix='/api/v1')
main_router.include_router(
    endpoints.dish_router,
    prefix='/dishes',
    tags=['Dishes'],
)

main_router.include_router(
    endpoints.slot_router,
    prefix='/cafes/{cafe_id}/time_slots',
    tags=['TimeSlots'],
)

main_router.include_router(
    endpoints.table_router,
    prefix='/cafes/{cafe_id}/tables',
    tags=['Tables'],
)

main_router.include_router(
    endpoints.media_router,
    prefix='/media',
    tags=['Media'],
)

main_router.include_router(
    endpoints.action_router,
    prefix='/actions',
    tags=['Actions'],
)

main_router.include_router(
    endpoints.cafe_router,
    prefix='/cafes',
    tags=['Cafes'],
)

main_router.include_router(
    endpoints.user_router,
    prefix='/users',
    tags=['Users'],
)

main_router.include_router(
    endpoints.auth_router,
    prefix='/auth',
    tags=['Authenticaton'],
)
