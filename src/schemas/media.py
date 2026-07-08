"""Схемы медиа-файлов.

Модуль описывает выходную схему для загруженных изображений.

Схемы API:
   - `MediaInfo` — идентификатор сохранённого медиа-файла.

Не использует иерархию `BaseCreate` / `BaseInfo`: схема наследует `BaseModel`
и `FromAttributesMixin` напрямую.
"""

import uuid

from pydantic import BaseModel

from schemas.base import FromAttributesMixin


class MediaInfo(FromAttributesMixin, BaseModel):
    """Схема данных загруженного изображения."""

    media_id: uuid.UUID
