import uuid
from typing import Optional

from pydantic import Field

from src.core import constants as ct
from src.models import Action
from src.schemas import (
    BaseProjectCreate,
    BaseProjectInfo,
    CafeShortInfo,
)


class ActionBase(BaseProjectCreate):
    """Базовая схема для Action.

    * `description` - string;
    * `photo_id` - uuid;
    * `cafes_id` - list uuid.
    """

    photo_id: Optional[uuid.UUID] = None
    cafes_id: Optional[list[uuid.UUID]] = Field(
        None,
        description='ID кафе, в которых действует акция',
    )


class ActionCreate(ActionBase):
    """Схема для создания новой акции.

    * `description` - string;
    * `photo_id` - uuid;
    * `cafes_id` - list uuid.
    """

    cafes_id: Optional[list[uuid.UUID]] = Field(
        None,
        description='ID кафе, в которых действует акция',
    )
    description: str = Field(
        ...,
        max_length=ct.MAX_DESCRIPTION_LEN,
        min_length=ct.MIN_DESCRIPTION_LEN,
    )


class ActionUpdate(ActionBase):
    """Схема для обновления существующей акции.

    * `description` - string;
    * `photo_id` - uuid;
    * `cafes_id` - list uuid.
    * `is_active` - boolean.
    """

    photo_id: Optional[uuid.UUID] = Field(None)
    cafes_id: Optional[list[uuid.UUID]] = Field(None)
    description: Optional[str] = Field(
        None,
        max_length=ct.MAX_DESCRIPTION_LEN,
        min_length=ct.MIN_DESCRIPTION_LEN,
    )
    is_active: Optional[bool] = None


class ActionInfo(BaseProjectInfo):
    """Схема с полной информацией об акции для ответа API.

    * `id` - int;
    * `description` - string;
    * `photo_id` - uuid;
    * `cafes` - list;
    * `is_active` - boolean;
    * `created_at` - date-time;
    * `updated_at` - date-time.
    """

    photo_id: Optional[uuid.UUID] = None
    cafes: list[CafeShortInfo] = Field(
        default_factory=list,
        description='Список кафе, где действует акция',
    )

    @classmethod
    def from_orm_model(cls, action: Action) -> 'ActionInfo':
        """Создает схему из ORM модели Action."""
        return cls.model_validate(action)
