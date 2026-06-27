import time

from fastapi import status
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.requests import Request
from starlette.responses import Response

from core.logger import bookingseats_logger


# TODO: чтобы залогировать данные о пользователе - нужна доработка.
class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования HTTP-запросов."""

    async def dispatch(
        self,
        request: Request,
        # для вызова ендпоинта
        call_next: RequestResponseEndpoint,
    ) -> Response:
        """Залогирует метод, статус и время выполнения запроса."""
        start_time = time.perf_counter()
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        # пробуем вызввать ендпойнт, записываем статус возвращаем ответ
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        # при любом исходе записываем время, метод, url, статус в лог
        finally:
            duration_ms = (time.perf_counter() - start_time) * 1000
            bookingseats_logger.info(
                f'{request.method} {request.url.path} | '
                f'status={status_code} | '
                f'{duration_ms:.2f}ms',
            )
