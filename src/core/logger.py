"""Логирование в проекте BookingSeats.

Как устроено
-------------
- ``core/constants.py`` — уровень, формат, путь к файлу, ротация.
- ``core/logger.py`` — создание и экспорт ``bookingseats_logger``.
- ``main.py`` — middleware и логи жизненного цикла.
- ``core/logging_middleware.py`` — лог каждого HTTP-запроса.
- ``core/error_handlers.py`` — лог ошибок API.
- ``crud/base.py`` — лог операций с БД. (также можно указывать логирование
    в crud методах фичей).

Поле ``{extra[user]}`` — идентификатор контекста. Сейчас по умолчанию
``SYSTEM``. После внедрения авторизации сюда можно подставлять логин
или id пользователя через ``logger.bind(user=...)``.

Логирование по слоям
--------------------

1. Жизненный цикл (``main.py``)
   В ``lifespan`` пишутся события старта и остановки. Уровень: ``info``.

2. HTTP-слой (``core/logging_middleware.py``)
   ``LoggingMiddleware`` подключён в ``main.py``. В блоке ``finally``
   пишет метод, путь, статус и время выполнения. Уровень: ``info``.
   TODO: добавить данные о текущем пользователе.

3. Слой ошибок (``core/error_handlers.py``)
   - ``BookingSeatsAppError`` — ``error``
   - ``HTTPException`` — ``warning``
   - ``RequestValidationError`` — ``warning``
   - прочие ``Exception`` — ``error``
   Для бизнес-ошибок бросайте ``BookingSeatsAppError`` — обработчик
   сам залогирует и вернёт ``CustomError``.

4. Слой CRUD (``crud/base.py``)
   ``CRUDBase`` логирует на уровне ``debug``.

5. Эндпойнты и сервисы
   Сейчас логируют middleware и error handlers. Точечные записи::

       bookingseats_logger.debug('...')
       bookingseats_logger.warning('...')
       bookingseats_logger.error('...')
"""

import sys

from loguru import logger

from core.constants import (
    LOG_FILE,
    LOG_FILE_BACKUP_COUNT,
    LOG_FILE_MAX_SIZE,
    LOG_FORMAT,
    LOG_LEVEL,
)

logger.remove()


def setup_logger() -> None:
    """Вернет настроенный логер."""
    logger.add(
        sys.stdout,
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        colorize=True,
    )
    logger.add(
        LOG_FILE,
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        rotation=LOG_FILE_MAX_SIZE,
        retention=LOG_FILE_BACKUP_COUNT,
    )
    logger.bind(user='SYSTEM')
    return logger


bookingseats_logger = setup_logger()
