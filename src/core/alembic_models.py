"""Модели для Alembic autogenerate.

Модуль импортирует все ORM-модели и association tables для миграций.
"""

from src.core.base_model import Base
from src.models import (
    Action,
    Booking,
    BookingDish,
    BookingItem,
    Cafe,
    Dish,
    Slot,
    Table,
    User,
    cafe_actions,
    cafe_dishes,
)

__all__ = [
    'Base',
    'Action',
    'Booking',
    'BookingDish',
    'BookingItem',
    'Cafe',
    'Dish',
    'Slot',
    'Table',
    'User',
    'cafe_actions',
    'cafe_dishes',
]
