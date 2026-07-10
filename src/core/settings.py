from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Настройки приложения."""

    # Общие настройки
    title: str = 'Приложение BookingSeats команды № 4 потока 68-69'
    version: str = '0.0.1'
    description: str = (
        'Приложение для управления бронированием мест в кафе. '
        'Предоставляет REST API для управления данными о кафе, блюдах, столах и бронированиях.'
    )

    # Настройки подключения к БД
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_server: str = 'localhost'
    postgres_port: int = 5432

    # Настройки Redis
    redis_host: str = 'localhost'
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None

    # Настройки кеширования
    cache_expire_menu: int = 300
    cache_expire_actions: int = 600

    # Настройки Celery
    rabbitmq_host: str = 'rabbitmq'
    rabbitmq_port: int = 5672
    rabbitmq_password: str = 'guest'
    rabbitmq_user: str = 'guest'

    # Настройки напоминаний
    reminder_minutes_before: int = 30

    # Настройки для SMTP
    smtp_server: str = 'smtp.gmail.com'
    smtp_port: int = 587
    email_address: str = ''
    email_password: str = ''

    # Флаг для отключения автосоздания пользователей
    create_default_users: bool = False

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / '../infra/.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )

    @property
    def db_url(self) -> str:
        """Строка подключения к БД."""
        return (
            f'postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@'
            f'{self.postgres_server}:{self.postgres_port}/{self.postgres_db}'
        )

    @property
    def redis_url(self) -> str:
        """Строка подключения к Redis."""
        if self.redis_password:
            return f'redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}'
        return f'redis://{self.redis_host}:{self.redis_port}/{self.redis_db}'

    @property
    def rabbitmq_url(self) -> str:
        """Строка подключения к rabbitmq."""
        return (
            f'amqp://{self.rabbitmq_user}:{self.rabbitmq_password}@'
            f'{self.rabbitmq_host}:{self.rabbitmq_port}//'
        )


settings = Settings()  # type: ignore
