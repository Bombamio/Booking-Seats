"""Store slot start/end as TIME without timezone.

Revision ID: c8d1e4f2a6b3
Revises: 7b4e2f1c9a0d
Create Date: 2026-07-08 06:20:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'c8d1e4f2a6b3'
down_revision: Union[str, Sequence[str], None] = '7b4e2f1c9a0d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Переводит поля слотов с timestamptz на time."""
    op.drop_constraint('check_slot_time_order', 'slots', type_='check')
    op.alter_column(
        'slots',
        'start_time',
        existing_type=sa.DateTime(timezone=True),
        type_=sa.Time(),
        postgresql_using='start_time::time',
        existing_nullable=False,
    )
    op.alter_column(
        'slots',
        'end_time',
        existing_type=sa.DateTime(timezone=True),
        type_=sa.Time(),
        postgresql_using='end_time::time',
        existing_nullable=False,
    )
    op.create_check_constraint(
        'check_slot_time_order',
        'slots',
        'end_time > start_time',
    )


def downgrade() -> None:
    """Возвращает timestamptz для полей слотов."""
    op.drop_constraint('check_slot_time_order', 'slots', type_='check')
    op.alter_column(
        'slots',
        'start_time',
        existing_type=sa.Time(),
        type_=sa.DateTime(timezone=True),
        postgresql_using="('1970-01-01'::date + start_time) AT TIME ZONE 'UTC'",
        existing_nullable=False,
    )
    op.alter_column(
        'slots',
        'end_time',
        existing_type=sa.Time(),
        type_=sa.DateTime(timezone=True),
        postgresql_using="('1970-01-01'::date + end_time) AT TIME ZONE 'UTC'",
        existing_nullable=False,
    )
    op.create_check_constraint(
        'check_slot_time_order',
        'slots',
        'end_time > start_time',
    )
