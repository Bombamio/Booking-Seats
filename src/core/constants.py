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

################################################################################
# Описание ошибок для OpenApi в endpoints                                      #
################################################################################

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
        'description': ' Ошибка валидации данных',
    },
}

ERRORS_GET = {**ERROR_404, **ERROR_403}
ERRORS_GET_MULTI = {**ERROR_403, **ERROR_422}
ERRORS_CREATE = {**ERROR_400, **ERROR_403, **ERROR_422}
ERRORS_UPDATE = {**ERROR_400, **ERROR_403, **ERROR_404, **ERROR_422}
