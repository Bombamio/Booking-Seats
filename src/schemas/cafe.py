"""Схемы кафе.

Модуль описывает входные и выходные схемы для управления кафе и их менеджерами.

Локальные миксины:
   - `CafeBaseMixin` — название, адрес и телефон кафе.

Схемы API:
   - `CafeCreate` — создание кафе; `description` опционально.
   - `CafeUpdate` — частичное обновление; основные поля и `managers_id` не принимают `null`.
   - `CafeShortInfo` — краткая информация для вложенных ответов.
   - `CafeInfo` — полный ответ API со списком менеджеров.

Наследование:
   - входные схемы — `BaseDescriptionCreate` / `BaseDescriptionUpdate`;
   - выходные схемы — `BaseDescriptionShortInfo` / `BaseDescriptionInfo`;
   - `PhotoIdMixin` — опциональное изображение кафе.

Общие правила наследования и базовые миксины — в `src/schemas/base.py`.
"""

import uuid
from typing import ClassVar

from pydantic import Field

from src.core import constants as ct
from src.schemas.base import (
    BaseDescriptionCreate,
    BaseDescriptionInfo,
    BaseDescriptionShortInfo,
    BaseDescriptionUpdate,
    PhotoIdMixin,
)
from src.schemas.user import UserShortInfo


class CafeBaseMixin:
    """Миксин с атрибутами кафе.

    Поля:
        name (str): название кафе; обязательное.
        address (str): адрес кафе; обязательное.
        phone (str): телефон кафе; обязательное.
    """

    name: str = Field(
        max_length=ct.MAX_NAME_LEN,
        title='Название кафе',
        description='Можно вводить в любом регистре',
    )
    address: str = Field(
        max_length=ct.MAX_ADDRESS_LEN,
        title='Адрес кафе',
    )
    phone: str = Field(
        max_length=ct.MAX_PHONE_LEN,
        pattern=ct.PHONE_NUMBER_PATTERN,
        title='Телефон кафе',
    )


class CafeCreate(CafeBaseMixin, PhotoIdMixin, BaseDescriptionCreate):
    """Схема создания нового кафе.

    Поля (включая унаследованные):
        description (str | None): описание кафе; необязательное.
        name (str): название кафе; обязательное.
        address (str): адрес кафе; обязательное.
        phone (str): телефон кафе; обязательное.
        photo_id (UUID | None): идентификатор изображения; необязательное.
        managers_id (list[UUID]): идентификаторы менеджеров; необязательное.
    """

    managers_id: list[uuid.UUID] = Field(default_factory=list)


class CafeUpdate(PhotoIdMixin, BaseDescriptionUpdate):
    """Схема для обновления информации о кафе.

    Поля (включая унаследованные):
        description (str | None): описание кафе; необязательное.
        name (str | None): название кафе; необязательное; явный null запрещён.
        address (str | None): адрес кафе; необязательное; явный null запрещён.
        phone (str | None): телефон кафе; необязательное; явный null запрещён.
        photo_id (UUID | None): идентификатор изображения; необязательное.
        is_active (bool | None): признак активности; необязательное; явный null запрещён.
        managers_id (list[UUID] | None): идентификаторы менеджеров; необязательное; явный null запрещён.
    """

    name: str | None = Field(
        None,
        max_length=ct.MAX_NAME_LEN,
        title='Название кафе',
        description='Можно вводить в любом регистре',
    )
    address: str | None = Field(
        None,
        max_length=ct.MAX_ADDRESS_LEN,
        title='Адрес кафе',
    )
    phone: str | None = Field(
        None,
        max_length=ct.MAX_PHONE_LEN,
        pattern=ct.PHONE_NUMBER_PATTERN,
        title='Телефон кафе',
    )
    managers_id: list[uuid.UUID] | None = None

    _not_null_fields: ClassVar[set[str]] = {'name', 'address', 'phone', 'managers_id', 'is_active'}


class CafeShortInfo(CafeBaseMixin, PhotoIdMixin, BaseDescriptionShortInfo):
    """Схема с краткой информацией о кафе.

    Поля (включая унаследованные):
        description (str | None): описание кафе.
        is_active (bool | None): признак активности.
        id (UUID): идентификатор кафе.
        name (str): название кафе.
        address (str): адрес кафе.
        phone (str): телефон кафе.
        photo_id (UUID | None): идентификатор изображения.
    """


class CafeInfo(CafeBaseMixin, PhotoIdMixin, BaseDescriptionInfo):
    """Схема с полной информацией о кафе.

    Поля (включая унаследованные):
        description (str | None): описание кафе.
        is_active (bool | None): признак активности.
        id (UUID): идентификатор кафе.
        created_at (datetime): дата создания.
        updated_at (datetime): дата обновления.
        name (str): название кафе.
        address (str): адрес кафе.
        phone (str): телефон кафе.
        photo_id (UUID | None): идентификатор изображения.
        managers (list[UserShortInfo]): менеджеры кафе.
    """

    managers: list[UserShortInfo] = Field(default_factory=list)
