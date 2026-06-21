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
