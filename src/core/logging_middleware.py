"""Middleware логирования HTTP-запросов.

Модуль описывает запись метода, пути, статуса и времени выполнения каждого запроса.

Классы:
   - `LoggingMiddleware` — Starlette middleware для access-логов.

Примечание: данные о пользователе в middleware пока не логируются — только в
``get_current_user`` через ``current_user_var``.
"""

import time

from fastapi import status
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.requests import Request
from starlette.responses import Response

from src.core import constants as ct
from src.core.logger import bookingseats_logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования HTTP-запросов."""

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        """Залогирует метод, статус и время выполнения запроса."""
        start_time = time.perf_counter()
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            duration_ms = (time.perf_counter() - start_time) * ct.MILLISECONDS_IN_SECOND
            bookingseats_logger.info(
                f'{request.method} {request.url.path} | status={status_code} | {duration_ms:.2f}ms',
            )
