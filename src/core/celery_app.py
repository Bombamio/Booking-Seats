from celery import Celery

from src.core.settings import settings


class CeleryConfig:
    """Конфигурация celery."""

    enable_utc = True
    timezone = 'Europe/Moscow'


celery_app = Celery(
    'booking_seats',
    broker=settings.rabbitmq_url,
    # backend=settings.redis_url,
    include=['src.tasks.notifications', 'src.tasks.reminders'],
)


celery_app.config_from_object(CeleryConfig)
