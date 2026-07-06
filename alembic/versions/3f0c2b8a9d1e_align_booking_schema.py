"""Align booking schema with booking API.

Revision ID: 3f0c2b8a9d1e
Revises: b0be9c9f220a
Create Date: 2026-07-05 06:15:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '3f0c2b8a9d1e'
down_revision: Union[str, Sequence[str], None] = 'b0be9c9f220a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'bookings',
        sa.Column(
            'guest_number',
            sa.Integer(),
            server_default=str(1),
            nullable=False,
        ),
    )
    op.alter_column('bookings', 'guest_number', server_default=None)

    op.create_table(
        'booking_dishes',
        sa.Column('booking_id', sa.UUID(), nullable=False),
        sa.Column('dish_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['dish_id'], ['dishes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('booking_id', 'dish_id'),
    )

    op.execute("ALTER TYPE bookingstatus RENAME VALUE 'PENDING' TO 'BOOKING'")
    op.execute("ALTER TYPE bookingstatus RENAME VALUE 'CONFIRMED' TO 'ACTIVE'")
    op.execute("ALTER TYPE bookingstatus RENAME VALUE 'CANCELLED' TO 'CANCELED'")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TYPE bookingstatus RENAME VALUE 'CANCELED' TO 'CANCELLED'")
    op.execute("ALTER TYPE bookingstatus RENAME VALUE 'ACTIVE' TO 'CONFIRMED'")
    op.execute("ALTER TYPE bookingstatus RENAME VALUE 'BOOKING' TO 'PENDING'")

    op.drop_table('booking_dishes')
    op.drop_column('bookings', 'guest_number')
