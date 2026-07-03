from fastapi import status

from src.schemas import CustomError

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
# для Users описание не подходит, поэтому не используем
ERROR_422 = {
    status.HTTP_422_UNPROCESSABLE_ENTITY: {
        'model': CustomError,
        'description': 'Ошибка валидации данных',
    },
}
ERROR_422_MEDIA_SAVE = {
    status.HTTP_422_UNPROCESSABLE_ENTITY: {
        'model': CustomError,
        'description': 'Ошибка сохранения файла',
    },
}
ERROR_422_AUTH = {
    status.HTTP_422_UNPROCESSABLE_ENTITY: {
        'model': CustomError,
        'description': 'Неверные имя пользователя или пароль',
    },
}

# группы ошибок, собранные под методы эндпойнтов

# для всех GET(multi) кроме USERS, TABLE и TIME_SLOTS
ERRORS_GET_MULTI = {**ERROR_401, **ERROR_422}

# для GET(multi) у TABLE и TIME_SLOTS
ERRORS_GET_MULTI_WITH_404 = {**ERRORS_GET_MULTI, **ERROR_404}

ERRORS_POST_BOOKING = {**ERROR_400, **ERROR_401, **ERROR_422}

# для POST кроме BOOKING, TABLE, TIME_SLOTS, USERS и AUTH
ERRORS_POST = {**ERRORS_POST_BOOKING, **ERROR_403}

# для всех PATCH кроме ME, для всех GET(id) кроме USERS и ME,
# для POST у TABLE и TIME_SLOTS
ERRORS_4XX_FULL = {**ERRORS_POST, **ERROR_404}

# группа, отличающаяся для USER
ERRORS_GET_MULTI_USERS = {**ERROR_401, **ERROR_403, **ERROR_422}
ERRORS_PATCH_ME = {**ERROR_400, **ERROR_403, **ERROR_422}
ERRORS_GET_USERS = {**ERROR_401, **ERROR_403, **ERROR_404, **ERROR_422}

# для GET и POST у MEDIA
ERRORS_GET_MEDIA = {**ERROR_404, **ERROR_422}
ERRORS_POST_MEDIA = {**ERROR_400, **ERROR_401, **ERROR_403, **ERROR_422_MEDIA_SAVE}
