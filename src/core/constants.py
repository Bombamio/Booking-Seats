from pathlib import Path

PHONE_NUMBER_PATTERN = r'^\+?[0-9]{7,15}$'
# Основные числа: 1, 8, 16, 32, 64, 128, 256, 512, 1024, и т.д.
SECRET_KEY = 'bd125ffa58cbb4303de365029c44cdda23830f7181e18d158cc3e95d6b55c963'
# Пока будет здесь, сгенерирован с помощью команды в терминале:
# openssl rand -hex 32
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30
DEFAULT_GUEST_NUMBER = 1
MIN_DISH_QUANTITY = 1
MILLISECONDS_IN_SECOND = 1000
OPENAPI_TAGS = [
    {
        'name': 'Бронирования',
        'description': 'Управление бронированиями',
    },
]

MAX_EMAIL_LEN = 256
MIN_USERNAME_LEN = 3
MAX_USERNAME_LEN = 32
MAX_PASS_HASH_LEN = 32
MIN_PASSWORD_LEN = 8
MAX_PASSWORD_LEN = 64
MAX_PHONE_LEN = 16
MAX_TG_ID_LEN = 32

HASH_TIME_COST = 1
HASH_MEMORY_COST = 51200  # 50 MB
HASH_PARALLELISM = 2
HASH_SALT_LEN = 16

MIN_SEATS = 1

MAX_NAME_LEN = 128
MIN_NAME_LEN = 1

MAX_DESCRIPTION_LEN = 256
MIN_DESCRIPTION_LEN = 1

MAX_ADDRESS_LEN = 256
MIN_ADDRESS_LEN = 5

MAX_FILE_SIZE = 5242880  # 5 мб.
ACTION_REPR_DESCRIPTION_PREVIEW_LEN = 30


###############################################################################
# Параметры для работы с медиа-файлами                                        #
###############################################################################

MEDIA_CHUNK_SIZE = 64 * 1024
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

###############################################################################
# Настройки логгера приложения.                                               #
###############################################################################

LOG_DIR = Path(__file__).resolve().parent.parent / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / 'app.log'
LOG_FILE_BACKUP_COUNT = 5
LOG_FILE_MAX_SIZE = 1024 * 1024 * 5  # 5 мб.
LOG_LEVEL = 'DEBUG'
LOG_FORMAT = (
    '<green>{time:YYYY-MM-DD HH:mm:ss}</green> | '
    '<level>{level}</level> | '
    '<cyan>{extra[user]}</cyan> | '
    '<level>{message}</level>'
)
