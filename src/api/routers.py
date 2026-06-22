from fastapi import APIRouter

from src.api.endpoints import (
    dish_router,
)

main_router = APIRouter(prefix='/api/vi')
main_router.include_router(
    dish_router,
    prefix='/dishes',
    tags=['Dishes'],
)
