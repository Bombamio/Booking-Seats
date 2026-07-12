"""Кеш Redis.

Модуль описывает асинхронное подключение и операции с кешем.

Классы:
   - `RedisCache` — set, delete и очистка по шаблону ключа.
"""

import json
from typing import Any

from redis import asyncio as aioredis

from src.core.settings import settings


class RedisCache:
    """Класс для работы с Redis-кешем."""

    def __init__(self) -> None:
        """Инициализирует кеш без активного подключения."""
        self.redis = None

    async def connect(self) -> None:
        """Подключится к Redis при первом обращении."""
        if not self.redis:
            self.redis = await aioredis.from_url(settings.redis_url, decode_responses=True)

    async def set(
        self,
        key: str,
        value: Any,
        expire: int | None = None,
    ) -> None:
        """Сохранит данные в кеш с временем жизни."""
        await self.connect()
        ttl = expire if expire is not None else settings.cache_expire_menu
        await self.redis.setex(
            key,
            ttl,
            json.dumps(value, default=str),
        )

    async def delete(self, key: str) -> None:
        """Удалит данные из кеша по ключу."""
        await self.connect()
        await self.redis.delete(key)

    async def clear_pattern(self, pattern: str) -> None:
        """Очистит кеш по шаблону ключа."""
        await self.connect()
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)


cache = RedisCache()
