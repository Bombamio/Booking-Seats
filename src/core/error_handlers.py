"""Обработчики ошибок FastAPI.

Модуль описывает преобразование исключений в ответы ``CustomError``.

Функции:
   - обработчики ``BookingSeatsAppError``, ``HTTPException``,
     ``RequestValidationError`` и прочих исключений;
   - `register_error_handlers` — регистрация обработчиков в приложении.
"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.core.exceptions import BookingSeatsAppError
from src.core.logger import bookingseats_logger
from src.schemas.custom_error import CustomError


def build_error_response(code: int, message: str) -> JSONResponse:
    """Сформирует JSON-ответ с ошибкой в формате CustomError."""
    error = CustomError(code=code, message=message)
    return JSONResponse(
        status_code=code,
        content=error.model_dump(),
    )


async def booking_seats_app_error_handler(
    request: Request,
    exc: BookingSeatsAppError,
) -> JSONResponse:
    """Вернёт ответ с ошибкой в формате CustomError для BookingSeatsAppError."""
    bookingseats_logger.error(f'BookingSeatsAppError: {exc.code} {exc.message}')
    return build_error_response(exc.code, exc.message)


async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    """Вернёт ответ с ошибкой в формате CustomError для HTTPException."""
    message = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    bookingseats_logger.warning(
        f'HTTPException: {message} | URL: {request.url} | Status code: {exc.status_code}',
    )
    return build_error_response(exc.status_code, message)


async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Вернёт ответ с ошибкой для RequestValidationError.

    Сообщение собирается из фрагментов, которые формирует FastAPI.
    """
    message = '; '.join(
        f'{" -> ".join(str(loc) for loc in error["loc"])}: {error["msg"]}' for error in exc.errors()
    )
    bookingseats_logger.warning(
        f'RequestValidationError: {message} | URL: {request.url}',
    )
    return build_error_response(status.HTTP_422_UNPROCESSABLE_CONTENT, message)


async def internal_server_error_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Вернёт ответ с ошибкой для непредвиденных ошибок."""
    bookingseats_logger.error(
        f'Внутренняя ошибка сервера: {exc} | URL: {request.url}',
    )
    return build_error_response(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        'Внутренняя ошибка сервера',
    )


def register_error_handlers(app: FastAPI) -> None:
    """Зарегистрирует обработчики ошибок приложения."""
    app.add_exception_handler(
        BookingSeatsAppError,
        booking_seats_app_error_handler,
    )
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(
        RequestValidationError,
        validation_error_handler,
    )
    app.add_exception_handler(Exception, internal_server_error_handler)
