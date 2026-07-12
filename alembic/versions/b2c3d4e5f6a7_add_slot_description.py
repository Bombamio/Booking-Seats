"""add description to slots.

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-07-12 10:05:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Добавляет необязательное поле description в slots."""
    op.add_column(
        'slots',
        sa.Column('description', sa.String(length=256), nullable=True),
    )


def downgrade() -> None:
    """Удаляет поле description из slots."""
    op.drop_column('slots', 'description')
