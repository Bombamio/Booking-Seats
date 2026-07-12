"""Celery-задача уведомления администратора о бронировании.

Модуль описывает отправку email менеджеру при создании, изменении или отмене брони.

Задачи:
   - `notify_admin` — письмо с деталями события бронирования.
"""

from celery import Task

from src.core.celery_app import celery_app
from src.core.email import send_email

_BOOKING_EVENT_TITLES = {
    'created': 'Появилось новое бронирование',
    'updated': 'Изменено бронирование',
    'canceled': 'Отменено бронирование',
}


@celery_app.task(bind=True, max_retries=3)
def notify_admin(
    self: Task,
    event_type: str,
    cafe_name: str,
    booking_id: str,
    booking_date: str,
    slot_times: str,
    admin_email: str,
    username: str,
    user_email: str | None,
    user_phone: str | None,
) -> None:
    """Отправит менеджеру кафе email о событии бронирования."""
    title = _BOOKING_EVENT_TITLES.get(event_type, 'Событие бронирования')
    text_message = (
        f'{title}\n'
        f'ID бронирования: {booking_id}\n'
        f'Кафе: {cafe_name}\n'
        f'Дата: {booking_date}\n'
        f'Время слота: {slot_times}\n'
        f'Имя клиента: {username}\n'
        f'Контакты: email: {user_email or "не указан"}, телефон: {user_phone or "не указан"}'
    )
    try:
        send_email(text_message, admin_email)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60) from exc
