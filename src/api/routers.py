from fastapi import APIRouter

from src.api.endpoints import (
    dish_router,
    slot_router,
)

main_router = APIRouter(prefix='/api/vi')
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
