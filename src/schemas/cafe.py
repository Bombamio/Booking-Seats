import uuid  # noqa: I001

from pydantic import BaseModel, ConfigDict, Field

from src.core import constants as ct
from src.schemas.base import (
    BaseProjectCreate,
    BaseProjectInfo,
    BaseProjectShortInfo,
)
from src.schemas.user import UserShortInfo


class CafeBase(BaseModel):
    """Базовая абстрактная схема Cafe.

    * name: str (обязательное)
    * address: str (обязательное)
    * phone: str (обязательное)
    * photo_id: uuid.UUID (не обязательное)
    """

    __abstract__ = True
    model_config = ConfigDict(extra='forbid')

    name: str = Field(
        ..., min_length=ct.MIN_NAME_LEN, max_length=ct.MAX_NAME_LEN,
        title='Название кафе', description='Можно вводить в любом регистре',
    )
    address: str = Field(
        ..., max_length=ct.MAX_ADDRESS_LEN,
        title='Адрес кафе',
    )
    phone: str = Field(
        ...,
        max_length=ct.MAX_PHONE_LEN,
        pattern=ct.PHONE_NUMBER_PATTERN,
        title='Телефон кафе',
    )
    photo_id: uuid.UUID | None = None


class CafeShortInfo(CafeBase, BaseProjectShortInfo):
    """Схема с краткой информацией о кафе.

    * id: uuid.UUID (обязательное)
    * description: str (не обязательное)
    * name: str (обязательное)
    * address: str (обязательное)
    * phone: str (обязательное)
    * photo_id: uuid.UUID (не обязательное)
    """

    pass


class CafeInfo(CafeBase, BaseProjectInfo):
    """Схема с полной информацией о кафе.

    * id: uuid.UUID (обязательное)
    * description: str (не обязательное)
    * name: str  (обязательное)
    * address: str (обязательное)
    * phone: str (обязательное)
    * photo_id: uuid.UUID (не обязательное)
    * is_active: bool (обязательное)
    * created_at: datetime (обязательное)
    * updated_at: datetime (не обязательное)
    """

    managers: list[UserShortInfo] = Field(default_factory=list)


class CafeCreate(CafeBase, BaseProjectCreate):
    """Схема создания нового кафе.

    * name: str (обязательное)
    * description: str (не обязательное)
    * address: str (обязательное)
    * phone: str (обязательное)
    * photo_id: uuid.UUID (не обязательное)
    * managers_id: list[uuid.UUID] (не обязательное)
    """

    managers_id: list[uuid.UUID] = Field(default_factory=list)


class CafeUpdate(BaseModel):
    """Схема для обновления информации о кафе.

    * name: str (не обязательное)
    * description: str (не обязательное)
    * address: str (не обязательное)
    * phone: str (не обязательное)
    * photo_id: uuid.UUID (не обязательное)
    * managers_id: list[uuid.UUID] (не обязательное)
    * is_active: bool (не обязательное)
    """

    model_config = ConfigDict(extra='forbid')

    name: str | None = Field(
        None, min_length=ct.MIN_NAME_LEN, max_length=ct.MAX_NAME_LEN,
        title='Название кафе', description='Можно вводить в любом регистре',
    )
    address: str | None = Field(
        None, max_length=ct.MAX_ADDRESS_LEN,
        title='Адрес кафе',
    )
    phone: str | None = Field(
        None,
        max_length=ct.MAX_PHONE_LEN,
        pattern=ct.PHONE_NUMBER_PATTERN,
        title='Телефон кафе',
    )
    photo_id: uuid.UUID | None = None

    managers_id: list[uuid.UUID] | None = None

    is_active: bool | None = None
