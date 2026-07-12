"""Схемы ошибок OpenAPI для эндпоинтов API.

Модуль описывает переиспользуемые группы HTTP-ответов с ошибками.

Базовые коды:
   - `ERROR_400` — ошибка в параметрах запроса;
   - `ERROR_401` — неавторизованный пользователь;
   - `ERROR_403` — доступ запрещён;
   - `ERROR_404` — данные не найдены;
   - `ERROR_422` — ошибка валидации данных;
   - `ERROR_422_MEDIA_SAVE` — ошибка сохранения файла;
   - `ERROR_422_AUTH` — неверные имя пользователя или пароль.

Группы для эндпоинтов:
   - `ERRORS_GET_MULTI` — GET (список), кроме users, tables и time_slots;
   - `ERRORS_GET_MULTI_WITH_404` — GET (список) для tables и time_slots;
   - `ERRORS_POST_BOOKING` — POST бронирования;
   - `ERRORS_POST` — POST, кроме booking, table, time_slots, users и auth;
   - `ERRORS_4XX_FULL` — PATCH, GET по id, POST table и time_slots;
   - `ERRORS_AUTH`, `ERRORS_POST_USERS`, `ERRORS_GET_MULTI_USERS` и др. — users;
   - `ERRORS_POST_CAFE` — кафе;
   - `ERRORS_GET_MEDIA`, `ERRORS_POST_MEDIA` — медиа.
"""

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

ERRORS_GET_MULTI = {**ERROR_401, **ERROR_422}

ERRORS_GET_MULTI_WITH_404 = {**ERRORS_GET_MULTI, **ERROR_404}

ERRORS_POST_BOOKING = {**ERROR_400, **ERROR_401, **ERROR_422}

ERRORS_POST = {**ERRORS_POST_BOOKING, **ERROR_403}

ERRORS_4XX_FULL = {**ERRORS_POST, **ERROR_404}

ERRORS_AUTH = {**ERROR_422_AUTH}
ERRORS_POST_USERS = {**ERROR_400, **ERROR_422}
ERRORS_GET_MULTI_USERS = {**ERROR_401, **ERROR_403, **ERROR_422}
ERRORS_PATCH_ME = {**ERROR_400, **ERROR_403, **ERROR_422}
ERRORS_GET_USERS = {**ERROR_401, **ERROR_403, **ERROR_404, **ERROR_422}
ERRORS_GET_ME = {**ERROR_401}
ERRORS_UPDATE_ME = {**ERROR_400, **ERROR_401, **ERROR_422}

ERRORS_POST_CAFE = {**ERRORS_POST, **ERROR_404}

ERRORS_GET_MEDIA = {**ERROR_404, **ERROR_422}
ERRORS_POST_MEDIA = {**ERROR_400, **ERROR_401, **ERROR_403, **ERROR_422_MEDIA_SAVE}
