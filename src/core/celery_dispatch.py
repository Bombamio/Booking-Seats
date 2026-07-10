"""Постановка Celery-задач с переводом сбоев брокера в BookingSeatsCeleryError."""

from collections.abc import Callable
from typing import TypeVar

from kombu.exceptions import OperationalError as KombuOperationalError

from src.core.exceptions import BookingSeatsCeleryError

T = TypeVar('T')

_CELERY_DISPATCH_ERRORS = (
    KombuOperationalError,
    ConnectionError,
    OSError,
)


def dispatch_celery_task(dispatch: Callable[[], T]) -> T:
    """Выполнит постановку Celery-задачи и переведёт сбой брокера в BookingSeatsCeleryError."""
    try:
        return dispatch()
    except _CELERY_DISPATCH_ERRORS as exc:
        raise BookingSeatsCeleryError(
            f'Фоновая задача не поставлена в очередь: {exc}',
        ) from exc


def revoke_celery_task(task_id: str) -> None:
    """Отзовёт Celery-задачу по ID (например, отложенное напоминание)."""
    from src.core.celery_app import celery_app

    try:
        celery_app.control.revoke(task_id, terminate=False)
    except _CELERY_DISPATCH_ERRORS as exc:
        raise BookingSeatsCeleryError(
            f'Фоновая задача {task_id} не отозвана: {exc}',
        ) from exc
