from celery import Task

from src.core.celery_app import celery_app
from src.core.email import send_email


@celery_app.task(bind=True, max_retries=3)
def send_reminder(
    self: Task,
    cafe_name: str,
    booking_date: str,
    slot_times: str,
    username: str,
    user_email: str,
) -> None:
    """Задача для напоминания пользователю о бронировании."""
    text_message = (
        f'Уважаемый(ая) {username}, напоминаем Вам о бронировании:\n'
        f'Кафе: {cafe_name}\n'
        f'Дата: {booking_date}\n'
        f'Время: {slot_times}\n'
    )
    try:
        send_email(text_message, user_email)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
