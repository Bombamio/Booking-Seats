from celery import Task

from src.core.celery_app import celery_app
from src.core.email import send_email


@celery_app.task(bind=True, max_retries=3)
def notify_admin(
    self: Task,
    cafe_name: str,
    booking_date: str,
    admin_email: str,
    username: str,
    user_email: str,
    user_phone: str,
) -> None:
    """Задача для уведомления менеджера кафе."""
    text_message = (
        f'Появилось новое бронирование\n'
        f'Кафе: {cafe_name}\n'
        f'Дата: {booking_date}\n'
        f'Имя клиента: {username}\n'
        f'Контакты: email: {user_email}, телефон: {user_phone}'
    )
    try:
        send_email(text_message, admin_email)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@celery_app.task()
def test_notification() -> None:
    """Тест уведомлений."""
    print('получилось')
