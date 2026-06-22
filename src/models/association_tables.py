# feature/actions/Artur
from sqlalchemy import Column, ForeignKey, String, Table

from src.core.base_model import Base

action_cafes = Table(
    'action_cafes',
    Base.metadata,
    Column(
        'action_id',
        String(36),
        ForeignKey('actions.id', ondelete='CASCADE'),
        primary_key=True,
    ),
    Column(
        'cafe_id',
        String(36),
        ForeignKey('cafes.id', ondelete='CASCADE'),
        primary_key=True,
    ),
)

# ===
from sqlalchemy import Column, ForeignKey, Table

from src.core.base_model import Base

cafe_dishes = Table(
    'cafe_dishes',
    Base.metadata,
    Column('cafe_id', ForeignKey('cafes.id'), primary_key=True),
    Column('dishes_id', ForeignKey('dishes.id'), primary_key=True),
)
cafe_actions = Table(
    'cafe_actions',
    Base.metadata,
    Column('cafe_id', ForeignKey('cafes.id'), primary_key=True),
    Column('action_id', ForeignKey('actions.id'), primary_key=True),
)
booking_dishes = Table(...)
