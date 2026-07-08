from sqlalchemy import Column, ForeignKey, Table

from src.core.base_model import Base

cafe_dishes = Table(
    'cafe_dishes',
    Base.metadata,
    Column('cafe_id', ForeignKey('cafes.id', ondelete='RESTRICT'), primary_key=True),
    Column('dishes_id', ForeignKey('dishes.id', ondelete='RESTRICT'), primary_key=True),
)
cafe_actions = Table(
    'cafe_actions',
    Base.metadata,
    Column('cafe_id', ForeignKey('cafes.id', ondelete='RESTRICT'), primary_key=True),
    Column('action_id', ForeignKey('actions.id', ondelete='RESTRICT'), primary_key=True),
)
