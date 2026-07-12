"""Ассоциативные таблицы many-to-many.

Описывает связующие таблицы между кафе и блюдами, а также между кафе и акциями.

Таблицы:
   - `cafe_dishes` — связь кафе и блюд.
   - `cafe_actions` — связь кафе и акций.
"""

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
