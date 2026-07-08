"""Схемы акции.

Модуль описывает входные и выходные схемы для управления акциями кафе.

Схемы API:
   - `ActionCreate` — создание акции; обязательные `description` и `cafes_id`.
   - `ActionUpdate` — частичное обновление; `description` и `is_active` не принимают `null`.
   - `ActionInfo` — полный ответ API со списком связанных кафе.

Наследование:
   - `ActionCreate` — `BaseDescriptionCreate`;
   - `ActionUpdate` / `ActionInfo` — `BaseDescriptionUpdate` / `BaseDescriptionInfo` и `PhotoIdMixin`.

Общие правила наследования и базовые миксины — в `src/schemas/base.py`.
"""

import uuid

from pydantic import Field

from src.core import constants as ct
from src.schemas.base import BaseDescriptionCreate, BaseDescriptionInfo, BaseDescriptionUpdate, PhotoIdMixin
from src.schemas.cafe import CafeShortInfo


class ActionCreate(BaseDescriptionCreate):
    """Схема для создания новой акции.

    Поля (включая унаследованные):
        description (str): описание акции; обязательное.
        photo_id (UUID | None): идентификатор изображения; обязательное.
        cafes_id (list[UUID]): идентификаторы кафе-участников; обязательное.
    """

    photo_id: uuid.UUID | None
    cafes_id: list[uuid.UUID] = Field(description='Список идентификаторов кафе, участвующих в акции')
    description: str = Field(max_length=ct.MAX_DESCRIPTION_LEN)


class ActionUpdate(PhotoIdMixin, BaseDescriptionUpdate):
    """Схема для обновления акции.

    Поля (включая унаследованные):
        description (str | None): описание акции; необязательное; явный null запрещён.
        photo_id (UUID | None): идентификатор изображения; необязательное.
        is_active (bool | None): признак активности; необязательное; явный null запрещён.
        cafes_id (list[UUID] | None): идентификаторы кафе-участников; необязательное; явный null запрещён.
    """

    cafes_id: list[uuid.UUID] | None = None
    _not_null_fields: set[str] = {'cafes_id', 'description', 'is_active'}


class ActionInfo(PhotoIdMixin, BaseDescriptionInfo):
    """Схема с полной информацией об акции.

    Поля (включая унаследованные):
        description (str | None): описание акции.
        is_active (bool | None): признак активности.
        id (UUID): идентификатор акции.
        created_at (datetime): дата создания.
        updated_at (datetime): дата обновления.
        photo_id (UUID | None): идентификатор изображения.
        cafes (list[CafeShortInfo]): связанные кафе.
    """

    cafes: list[CafeShortInfo] = Field(description='Список кафе, участвующих в акции')
