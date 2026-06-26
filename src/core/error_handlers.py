from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from schemas.custom_error import CustomError

from core.exceptions import BookingSeatsAppError


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
    """Вернет ответ с ошибкой в формате CustomError для BookingSeatsAppError."""
    return build_error_response(exc.code, exc.message)


async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    """Вернет ответ с ошибкой в формате CustomError для HTTPException."""
    message = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return build_error_response(exc.status_code, message)


async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Вернет ответ с ошибкой для RequestValidationError."""
    #  не мы задаем сообщение, его генерит FastAPI, надо выдать его в строку
    #  для этого складываем красиво из тех кусочков, что выдает FastAPI
    message = '; '.join(
        f"{' -> '.join(str(loc) for loc in error['loc'])}: {error['msg']}"
        for error in exc.errors()
    )
    return build_error_response(status.HTTP_422_UNPROCESSABLE_ENTITY, message)


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
