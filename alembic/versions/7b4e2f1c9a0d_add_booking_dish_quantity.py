"""Add quantity to booking dishes.

Revision ID: 7b4e2f1c9a0d
Revises: 3f0c2b8a9d1e
Create Date: 2026-07-05 07:33:30.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '7b4e2f1c9a0d'
down_revision: Union[str, Sequence[str], None] = '3f0c2b8a9d1e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'booking_dishes',
        sa.Column('quantity', sa.Integer(), server_default='1', nullable=False),
    )
    op.create_check_constraint(
        'check_booking_dish_quantity',
        'booking_dishes',
        'quantity > 0',
    )
    op.alter_column('booking_dishes', 'quantity', server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        'check_booking_dish_quantity',
        'booking_dishes',
        type_='check',
    )
    op.drop_column('booking_dishes', 'quantity')
