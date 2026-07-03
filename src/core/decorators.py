from functools import wraps
from typing import Any, Dict, Optional


def with_error_responses(  # noqa: ANN201
    extra_responses: Optional[Dict[int, Dict[str, Any]]] = None,
):
    """Декоратор для добавления кастомных responses в OpenApi эндпоинта.

    Облегчает код эндпойнта, убирая описание ошибок для openapi в декоратор.

    Args:
        extra_responses: описания видов возвращаемых ошибок.

    Пример использования в endpoint:

    @with_error_responses(ERRORS_GET_MULTI)  # из api.error_responses
    async def get_users(self, request: Request) -> list[User]:
        return await self.user_service.get_users()

    """

    def decorator(func):  # noqa: ANN001, ANN202
        """Добавит описание ошибок в атрибут responses функции."""

        @wraps(func)
        async def wrapper(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202
            """Выполнит исходный endpoint без изменения поведения."""
            return await func(*args, **kwargs)

        if not hasattr(wrapper, 'responses'):
            wrapper.responses = {}
        if extra_responses:
            wrapper.responses.update(extra_responses)
        return wrapper

    return decorator
