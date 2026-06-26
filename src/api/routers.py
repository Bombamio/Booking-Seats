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
    endpoints.cafe_router,
    prefix='/cafes',
    tags=['Cafes'],
)
