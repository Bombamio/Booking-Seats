import json
from typing import Any, Optional
from redis import asyncio as aioredis
from src.core.settings import settings


class RedisCache:
    """Класс для работы с Redis кешем."""

    def __init__(self):
        """Инициализация кеша."""
        self.redis = None

    async def connect(self):
        """Подключение к Redis."""
        if not self.redis:
            self.redis = await aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )

    async def get(self, key: str) -> Optional[Any]:
        """Получение данных из кеша по ключу."""
        await self.connect()
        data = await self.redis.get(key)
        if data:
            return json.loads(data)
        return None

    async def set(self, key: str, value: Any, expire: int = 300):
        """Сохранение данных в кеш с временем жизни."""
        await self.connect()
        await self.redis.setex(
            key,
            expire,
            json.dumps(value, default=str)
        )

    async def delete(self, key: str):
        """Удаление данных из кеша по ключу."""
        await self.connect()
        await self.redis.delete(key)

    async def clear_pattern(self, pattern: str):
        """Очистка кеша по шаблону ключа."""
        await self.connect()
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)


cache = RedisCache()