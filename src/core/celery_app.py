"""Конфигурация Celery worker.

Модуль описывает приложение Celery, брокер RabbitMQ и единое логирование.

Классы:
   - `CeleryConfig` — часовой пояс и параметры worker.
"""

from celery import Celery
from celery.signals import setup_logging

from src.core.logger import bookingseats_logger  # noqa: F401
from src.core.logger import setup_logging as setup_app_logging
from src.core.settings import settings


class CeleryConfig:
    """Конфигурация Celery worker."""

    enable_utc = True
    timezone = 'Europe/Moscow'
    worker_hijack_root_logger = False
    worker_redirect_stdouts = False


@setup_logging.connect
def configure_celery_logging(**kwargs: object) -> None:
    """Подключит логи Celery worker к единому loguru-логгеру приложения."""
    setup_app_logging()


celery_app = Celery(
    'booking_seats',
    broker=settings.rabbitmq_url,
    include=['src.tasks.notifications', 'src.tasks.reminders'],
)


celery_app.config_from_object(CeleryConfig)
