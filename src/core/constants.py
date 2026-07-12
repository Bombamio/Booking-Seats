"""Константы проекта BookingSeats.

Модуль описывает лимиты валидации, параметры безопасности, медиа, логирования
и дефолтных пользователей.

Разделы:
   - аутентификация и JWT;
   - лимиты полей сущностей;
   - параметры Argon2;
   - медиафайлы;
   - логирование;
   - Celery и напоминания;
   - пользователи по умолчанию для сида.
"""

from pathlib import Path

BYTES_PER_KB = 1024
BYTES_PER_MB = 1024 * BYTES_PER_KB
UUID_STRING_LEN = 36
CELERY_TASK_MAX_RETRIES = 3
CELERY_TASK_RETRY_COUNTDOWN_SECONDS = 60
MEDIA_RGB_WHITE = (255, 255, 255)
LOGURU_INTERCEPT_STACK_DEPTH = 2
REQUEST_DURATION_DECIMAL_PLACES = 2
UVICORN_HOST = '0.0.0.0'
UVICORN_PORT = 8000

PHONE_NUMBER_PATTERN = r'^\+?[0-9]{7,15}$'
USER_PHONE_PATTERN = r'^\+\d{1,15}$'
USER_EMAIL_PATTERN = r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
SECRET_KEY = 'bd125ffa58cbb4303de365029c44cdda23830f7181e18d158cc3e95d6b55c963'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30
DEFAULT_GUEST_NUMBER = 1
MIN_DISH_QUANTITY = 1
MIN_TABLE_SLOT_COUNT = 1
MIN_CAFE_LINK_COUNT = 1
MILLISECONDS_IN_SECOND = 1000
OPENAPI_TAGS = [
    {
        'name': 'Аутентификация',
        'description': 'Получение данных для последующей авторизации',
    },
    {
        'name': 'Пользователи',
        'description': 'Управление пользователями',
    },
    {
        'name': 'Кафе',
        'description': 'Управление кафе',
    },
    {
        'name': 'Столы',
        'description': 'Управление столами в кафе',
    },
    {
        'name': 'Временные слоты',
        'description': 'Управление временными слотами',
    },
    {
        'name': 'Блюда',
        'description': 'Управление блюдами',
    },
    {
        'name': 'Акции',
        'description': 'Управление акциями',
    },
    {
        'name': 'Медиа',
        'description': 'Управление изображениями',
    },
    {
        'name': 'Бронирования',
        'description': 'Управление бронированиями',
    },
]

MAX_EMAIL_LEN = 320
MIN_USERNAME_LEN = 3
MAX_USERNAME_LEN = 32
MIN_PASSWORD_LEN = 8
MAX_PASSWORD_LEN = 64
MAX_PHONE_LEN = 16
MAX_TG_ID_LEN = 32

HASH_TIME_COST = 1
HASH_MEMORY_COST = 51200
HASH_PARALLELISM = 2
HASH_SALT_LEN = 16

MIN_SEATS = 1

MAX_NAME_LEN = 128
MIN_NAME_LEN = 1

MAX_DESCRIPTION_LEN = 256
MIN_DESCRIPTION_LEN = 1

MAX_ADDRESS_LEN = 256
MIN_ADDRESS_LEN = 5

MAX_FILE_SIZE = 5 * BYTES_PER_MB
ACTION_REPR_DESCRIPTION_PREVIEW_LEN = 30

MAX_DSC_LOG_LEN = 20

MEDIA_CHUNK_SIZE = 64 * BYTES_PER_KB
MEDIA_FILE_EXTENSION = '.jpg'
MEDIA_OUTPUT_TYPE = 'image/jpeg'
MEDIA_IMAGE_SIGNATURES = {
    b'\xff\xd8\xff': 'image/jpeg',
    b'\x89PNG\r\n\x1a\n': 'image/png',
}
MEDIA_SIGNATURE_CHECK_SIZE = max(len(signature) for signature in MEDIA_IMAGE_SIGNATURES)
ALLOWED_MEDIA_FORMATS = sorted({
    'jpg' if media_type.endswith('/jpeg') else media_type.rsplit('/', 1)[-1]
    for media_type in MEDIA_IMAGE_SIGNATURES.values()
})

MEDIA_DIR = Path(__file__).resolve().parent.parent / 'media'
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

LOG_DIR = Path(__file__).resolve().parent.parent / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / 'app.log'
LOG_FILE_BACKUP_COUNT = 5
LOG_FILE_MAX_SIZE = 5 * BYTES_PER_MB
LOG_LEVEL = 'DEBUG'
LOG_FORMAT = (
    '<green>{time:YYYY-MM-DD HH:mm:ss}</green> | '
    '<level>{level}</level> | '
    '<cyan>{extra[user]}</cyan> | '
    '<level>{message}</level>'
)
STDLIB_LOGGER_NAMES = (
    'uvicorn',
    'uvicorn.access',
    'uvicorn.error',
    'fastapi',
    'celery',
    'celery.task',
    'celery.worker',
    'celery.worker.consumer',
    'celery.worker.strategy',
    'celery.app.trace',
    'celery.redirected',
    'kombu',
    'amqp',
)

FIRST_SUPERUSER_USERNAME = 'admin_1'
FIRST_SUPERUSER_EMAIL = 'admin@example.com'
FIRST_SUPERUSER_PASSWORD = 'admin1234'

FIRST_MANAGER_USERNAME = 'manager_1'
FIRST_MANAGER_EMAIL = 'manager@example.com'
FIRST_MANAGER_PASSWORD = 'manager1234'

FIRST_USER_USERNAME = 'user_1'
FIRST_USER_EMAIL = 'user@example.com'
FIRST_USER_PASSWORD = 'user1234'
