import uuid

from pydantic import BaseModel


class MediaInfo(BaseModel):
    """Схема данных загруженного изображения."""

    media_id: uuid.UUID
