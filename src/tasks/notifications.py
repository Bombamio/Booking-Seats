from src.core.celery_app import celery_app


@celery_app.task
def test_notification() -> str:
    """Тестовая задача уведомления."""
    return 'Уведомление отправлено'
