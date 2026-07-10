"""add booking reminder_task_id.

Revision ID: a1b2c3d4e5f6
Revises: f51226158a61
Create Date: 2026-07-10 01:40:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '60db81819c57'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Добавляет колонку reminder_task_id в bookings."""
    op.add_column(
        'bookings',
        sa.Column('reminder_task_id', sa.String(length=36), nullable=True),
    )


def downgrade() -> None:
    """Удаляет колонку reminder_task_id из bookings."""
    op.drop_column('bookings', 'reminder_task_id')
