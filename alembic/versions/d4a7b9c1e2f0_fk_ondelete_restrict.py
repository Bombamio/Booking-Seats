"""Set RESTRICT on all foreign key delete rules.

Revision ID: d4a7b9c1e2f0
Revises: c8d1e4f2a6b3
Create Date: 2026-07-08 06:35:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'd4a7b9c1e2f0'
down_revision: Union[str, Sequence[str], None] = 'c8d1e4f2a6b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

FK_CHANGES = (
    ('booking_dishes', 'booking_dishes_booking_id_fkey', 'bookings', ['booking_id'], ['id']),
    ('booking_dishes', 'booking_dishes_dish_id_fkey', 'dishes', ['dish_id'], ['id']),
    ('bookingitems', 'bookingitems_booking_id_fkey', 'bookings', ['booking_id'], ['id']),
    ('bookingitems', 'bookingitems_slot_id_fkey', 'slots', ['slot_id'], ['id']),
    ('bookingitems', 'bookingitems_table_id_fkey', 'tables', ['table_id'], ['id']),
    ('bookings', 'bookings_cafe_id_fkey', 'cafes', ['cafe_id'], ['id']),
    ('bookings', 'bookings_user_id_fkey', 'users', ['user_id'], ['id']),
    ('cafe_actions', 'cafe_actions_action_id_fkey', 'actions', ['action_id'], ['id']),
    ('cafe_actions', 'cafe_actions_cafe_id_fkey', 'cafes', ['cafe_id'], ['id']),
    ('cafe_dishes', 'cafe_dishes_cafe_id_fkey', 'cafes', ['cafe_id'], ['id']),
    ('cafe_dishes', 'cafe_dishes_dishes_id_fkey', 'dishes', ['dishes_id'], ['id']),
    ('slots', 'slots_cafe_id_fkey', 'cafes', ['cafe_id'], ['id']),
    ('tables', 'tables_cafe_id_fkey', 'cafes', ['cafe_id'], ['id']),
    ('users', 'users_cafe_id_fkey', 'cafes', ['cafe_id'], ['id']),
)


def _set_ondelete(ondelete: str) -> None:
    for table, constraint, referred_table, local_cols, remote_cols in FK_CHANGES:
        op.drop_constraint(constraint, table, type_='foreignkey')
        op.create_foreign_key(
            constraint,
            table,
            referred_table,
            local_cols,
            remote_cols,
            ondelete=ondelete,
        )


def upgrade() -> None:
    """Запретит каскадное удаление по всем внешним ключам."""
    _set_ondelete('RESTRICT')


def downgrade() -> None:
    """Вернёт прежние правила удаления."""
    cascade_tables = {
        'booking_dishes_booking_id_fkey',
        'booking_dishes_dish_id_fkey',
        'bookingitems_booking_id_fkey',
        'bookingitems_slot_id_fkey',
        'bookingitems_table_id_fkey',
        'bookings_cafe_id_fkey',
        'bookings_user_id_fkey',
        'slots_cafe_id_fkey',
        'tables_cafe_id_fkey',
    }
    for table, constraint, referred_table, local_cols, remote_cols in FK_CHANGES:
        op.drop_constraint(constraint, table, type_='foreignkey')
        op.create_foreign_key(
            constraint,
            table,
            referred_table,
            local_cols,
            remote_cols,
            ondelete='CASCADE' if constraint in cascade_tables else None,
        )
