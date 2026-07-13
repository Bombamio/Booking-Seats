from src.core.settings import Settings


def test_db_url() -> None:
    """Тест URL БД."""
    settings = Settings(
        postgres_user='test_user',
        postgres_password='test_pass',
        postgres_db='test_db',
        postgres_server='localhost',
        postgres_port=5432,
    )
    assert settings.db_url == 'postgresql+asyncpg://test_user:test_pass@localhost:5432/test_db'


def test_redis_url_without_password() -> None:
    """Тест URL Redis без пароля."""
    settings = Settings(redis_host='localhost', redis_port=6379, redis_db=0, redis_password=None)
    assert settings.redis_url == 'redis://localhost:6379/0'


def test_redis_url_with_password() -> None:
    """Тест URL Redis с паролем."""
    settings = Settings(redis_host='localhost', redis_port=6379, redis_db=0, redis_password='secret')
    assert settings.redis_url == 'redis://:secret@localhost:6379/0'


def test_rabbitmq_url() -> None:
    """Проверка формирования RabbitMQ-URL без пароля и порта по умолчанию."""
    settings = Settings(
        rabbitmq_user='guest',
        rabbitmq_password='guest',
        rabbitmq_host='rabbitmq',
        rabbitmq_port=5672,
    )
    assert settings.rabbitmq_url == 'amqp://guest:guest@rabbitmq:5672//'
