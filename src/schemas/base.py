import uuid

from datetime import datetime

from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


# TODO: Нуждается в доработке.
class BaseProjectModel(BaseModel):
    """Базовая абстрактная модель для schemas сериализаторов."""

    __abstract__ = True

    model_config = ConfigDict(
        extra="forbid",
    )


# TODO: Нуждается в доработке.
class BaseProjectDB(BaseProjectModel):
    """Базовая абстрактная модель для сериализаторов db."""

    __abstract__ = True

    id: uuid.UUID
    create_date: datetime
    update_date: datetime

    model_config = ConfigDict(from_attributes=True)