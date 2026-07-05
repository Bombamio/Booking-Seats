from fastapi import APIRouter

from src.api.endpoints import (
    action_router,
    auth_router,
    cafe_router,
    dish_router,
    health_router,
    media_router,
    slot_router,
    table_router,
    user_router,
)

main_router = APIRouter(prefix='/api/v1')

main_router.include_router(health_router)

main_router.include_router(
    dish_router,
    prefix='/dishes',
    tags=['Dishes'],
)

main_router.include_router(
    slot_router,
    prefix='/cafes/{cafe_id}/time_slots',
    tags=['TimeSlots'],
)

main_router.include_router(
    table_router,
    prefix='/cafes/{cafe_id}/tables',
    tags=[{'name': 'Столы', 'description': 'Управление столами в кафе'}],
)

main_router.include_router(
    media_router,
    prefix='/media',
    tags=['Media'],
)

main_router.include_router(
    action_router,
    prefix='/actions',
    tags=['Actions'],
)

main_router.include_router(
    cafe_router,
    prefix='/cafes',
    tags=['Cafes'],
)

main_router.include_router(
    user_router,
    prefix='/users',
    tags=['Users'],
)

main_router.include_router(
    auth_router,
    prefix='/auth',
    tags=['Authenticaton'],
)
