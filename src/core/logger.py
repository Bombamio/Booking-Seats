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

Текущего пользователя получаем из контекста с помощью ContextVar.
Стандартный механизм логирования FastAPI и Uvicorn перехватываем и выдаем в
том формате, коорый принят в нашем приложении.

Логирование по слоям
--------------------

1. Жизненный цикл (``main.py``)
   В ``lifespan`` пишутся события старта и остановки. Уровень: ``info``.

2. HTTP-слой (``core/logging_middleware.py``)
   ``LoggingMiddleware`` подключён в ``main.py``. В блоке ``finally``
   пишет метод, путь, статус и время выполнения. Уровень: ``info``.
   В ``extra`` добавляем данные о текущем пользователе.

3. Слой ошибок (``core/error_handlers.py``)
   - ``BookingSeatsAppError`` — ``error``
   - ``HTTPException`` — ``warning``
   - ``RequestValidationError`` — ``warning``
   - прочие ``Exception`` — ``error``
   Для бизнес-ошибок бросайте ``BookingSeatsAppError`` — обработчик
   сам залогирует и вернёт ``CustomError``.

4. Слой CRUD (``crud/base.py``)
   ``CRUDBase`` логирует на уровне ``debug``.

5. Celery worker (``core/celery_app.py``)
   Сигнал ``setup_logging`` подключает stdlib-логгеры Celery к loguru.
   Встроенные обработчики Celery не используются — один формат и ``app.log``.

6. Эндпойнты и сервисы
   Сейчас логируют middleware и error handlers. Точечные записи::

       bookingseats_logger.debug('...')
       bookingseats_logger.warning('...')
       bookingseats_logger.error('...')
"""

import logging
import sys
from contextvars import ContextVar

from loguru import logger

from src.core.constants import (
    LOG_FILE,
    LOG_FILE_BACKUP_COUNT,
    LOG_FILE_MAX_SIZE,
    LOG_FORMAT,
    LOG_LEVEL,
    STDLIB_LOGGER_NAMES,
)

logger.remove()
current_user_var: ContextVar[str] = ContextVar(
    'current_user',
    default='SYSTEM',
)


def get_user() -> str:
    """Вернет текущего пользователя из контекста."""
    return current_user_var.get()


class InterceptHandler(logging.Handler):
    """Перехватчик логов из стандартного logging в loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        """Передаст сообщение в loguru."""
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = 'INFO'
        frame = logging.currentframe()
        depth = 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def configure_stdlib_logger(stdlib_logger: logging.Logger) -> None:
    """Подключит stdlib-логгер к loguru без дублирования."""
    stdlib_logger.handlers.clear()
    stdlib_logger.addHandler(InterceptHandler())
    stdlib_logger.propagate = False


def setup_logging() -> None:
    """Настроит перехват логов из стандартного logging в loguru."""
    logging.captureWarnings(True)
    logging.root.handlers.clear()
    logging.root.addHandler(InterceptHandler())
    logging.root.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    for name in STDLIB_LOGGER_NAMES:
        configure_stdlib_logger(logging.getLogger(name))

    try:
        from celery.utils.log import get_multiprocessing_logger

        mp_logger = get_multiprocessing_logger()
        if mp_logger is not None:
            configure_stdlib_logger(mp_logger)
    except ImportError:
        pass


def setup_logger() -> None:
    """Вернет настроенный логер."""
    logger.add(
        sys.stdout,
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        colorize=True,
        filter=lambda record: record['extra'].setdefault('user', get_user()),
    )
    logger.add(
        LOG_FILE,
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        rotation=LOG_FILE_MAX_SIZE,
        retention=LOG_FILE_BACKUP_COUNT,
        filter=lambda record: record['extra'].setdefault('user', get_user()),
    )
    setup_logging()
    return logger


bookingseats_logger = setup_logger()
