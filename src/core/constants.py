from pathlib import Path

from fastapi import status

from schemas.custom_error import CustomError

# Основные числа: 1, 8, 16, 32, 64, 128, 256, 512, 1024, и т.д.

MAX_EMAIL_LEN = 256
MAX_USERNAME_LEN = 32
MAX_PASS_HASH_LEN = 256
MAX_PHONE_LEN = 16
MAX_TG_ID_LEN = 32

MIN_SEATS = 1

MAX_NAME_LEN = 128
MIN_NAME_LEN = 1

MAX_DESCRIPTION_LEN = 256
MIN_DESCRIPTION_LEN = 1

MAX_ADDRESS_LEN = 256

MAX_FILE_SIZE = 5242880  # 5 мб.

###############################################################################
# Описание ошибок для OpenApi в endpoints                                     #
###############################################################################

ERROR_400 = {
    status.HTTP_400_BAD_REQUEST: {
        'model': CustomError,
        'description': 'Ошибка в параметрах запроса',
    },
}
ERROR_401 = {
    status.HTTP_401_UNAUTHORIZED: {
        'model': CustomError,
        'description': 'Неавторизированный пользователь',
    },
}
ERROR_403 = {
    status.HTTP_403_FORBIDDEN: {
        'model': CustomError,
        'description': 'Доступ запрещен',
    },
}
ERROR_404 = {
    status.HTTP_404_NOT_FOUND: {
        'model': CustomError,
        'description': 'Данные не найдены',
    },
}
#  для Users описание не подходит, поэтому не используем
ERROR_422 = {
    status.HTTP_422_UNPROCESSABLE_ENTITY: {
        'model': CustomError,
        'description': 'Ошибка валидации данных',
    },
}
ERROR_422_AUTH = {
    status.HTTP_422_UNPROCESSABLE_ENTITY: {
        'model': CustomError,
        'description': 'Неверные имя пользователя или пароль',
    },
}
# группы ошибок собранные под методы ендпойнтов.


# для всех GET(multi) кроме USERS, TABLE и TIME_SLOTS
ERRORS_GET_MULTI = {**ERROR_401, **ERROR_422}

# для GET(multi) у TABLE и TIME_SLOTS
ERRORS_GET_MULTI_WITH_404 = {**ERRORS_GET_MULTI, **ERROR_404}

ERRORS_POST_BOOKING = {**ERROR_400, **ERROR_401, **ERROR_422}

# для POST кроме BOOKING, TABLE, TIME_SLOTS, USERS и AUTH
ERRORS_POST = {**ERRORS_POST_BOOKING, **ERROR_403}

# для всех PATCH кроме ME, для всех GET(id) кроме USERS и ME, для POST у TABLE и TIME_SLOTS
ERRORS_4XX_FULL = {**ERRORS_POST, **ERROR_404}

# группа отличающихся для USER
ERRORS_GET_MULTI_USERS = {**ERROR_401, **ERROR_403, **ERROR_422}
ERRORS_PATCH_ME = {**ERROR_400, **ERROR_403, **ERROR_422}
ERRORS_GET_USERS = {**ERROR_401, **ERROR_403, **ERROR_404, **ERROR_422}

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
