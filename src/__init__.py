"""Пакет приложения BookingSeats.

Подавляет предупреждение Pydantic о затенении полей родительских миксинов в схемах.
"""

import warnings

warnings.filterwarnings(
    'ignore',
    message='Field name .* shadows an attribute in parent',
    category=UserWarning,
)
