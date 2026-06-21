from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field
from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.base_model import Base
from src.models.association_tables import action_cafes


class Action(Base):
    """Модель акции кафе."""

    __tablename__ = 'actions'

    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    description: Mapped[str] = mapped_column(Text, nullable=False)

    photos_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey('medias.id', ondelete='SET NULL'),
        nullable=True,
        comment='ID медиа-файла с изображением акции',
    )

    cafes = relationship(
        'Cafe',
        secondary=action_cafes,
        back_populates='actions',
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Action(id={self.id}, description='{self.description[:30]}...')>"


class ActionCreate(BaseModel):
    """Схема для создания новой акции."""

    description: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description='Описание акции',
        example='Счастливые часы: скидка 20% на все напитки с 12:00 до 16:00',
    )
    photos_id: Optional[str] = Field(
        None,
        max_length=36,
        description='ID медиа-файла (из таблицы Medias)',
        example='550e8400-e29b-41d4-a716-446655440000',
    )
    cafes_ids: List[str] = Field(
        ...,
        min_length=1,
        description='ID кафе, в которых действует акция',
        example=[
            '550e8400-e29b-41d4-a716-446655440001',
            '550e8400-e29b-41d4-a716-446655440002',
        ],
    )

    model_config = {'from_attributes': True}


class ActionUpdate(BaseModel):
    """Схема для обновления существующей акции."""

    description: Optional[str] = Field(
        None,
        min_length=1,
        max_length=5000,
        description='Новое описание акции',
    )
    photos_id: Optional[str] = Field(
        None,
        max_length=36,
        description='Новый ID медиа-файла',
    )
    cafes_ids: Optional[List[str]] = Field(
        None,
        min_length=1,
        description='Новый список ID кафе',
    )
    active: Optional[bool] = Field(
        None,
        description='Флаг активности акции',
    )

    model_config = {'from_attributes': True}


class CafeShortInfo(BaseModel):
    """Краткая информация о кафе для вложенных ответов."""

    id: str = Field(..., description='ID кафе')
    name: str = Field(..., description='Название кафе')

    model_config = {'from_attributes': True}


class ActionInfo(BaseModel):
    """Схема с полной информацией об акции для ответа API."""

    id: str = Field(..., description='Уникальный идентификатор акции')
    description: str = Field(..., description='Описание акции')
    photos_id: Optional[str] = Field(
        None,
        description='ID медиа-файла с изображением',
    )
    cafes: List[CafeShortInfo] = Field(
        default_factory=list,
        description='Список кафе, где действует акция',
    )
    active: bool = Field(..., description='Флаг активности акции')
    created_at: datetime = Field(
        ...,
        description='Дата и время создания записи',
    )
    updated_at: datetime = Field(
        ...,
        description='Дата и время последнего обновления записи',
    )

    model_config = {'from_attributes': True}

    @classmethod
    def from_orm_model(cls, action: Action) -> 'ActionInfo':
        """Создает схему из ORM модели Action."""
        return cls.model_validate(action)
