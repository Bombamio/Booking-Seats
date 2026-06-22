import enum
import uuid
from typing import List

from sqlalchemy import CheckConstraint, Enum, ForeignKey, String, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from src.core.base_model import Base
from src.core.constants import (MAX_LENGTH_EMAIL, MAX_LENGTH_PASS_HASH,
                                MAX_LENGTH_PHONE, MAX_LENGTH_USERNAME,
                                MAX_LENGTH_TG_ID)


class UserRole(enum.Enum):
    """Роли пользователей."""

    ADMIN = 'ADMIN'
    MANAGER = 'MANAGER'
    USER = 'USER'


class User(Base):
    """Модель пользователя."""

    username: Mapped[str] = mapped_column(
        String(MAX_LENGTH_USERNAME), unique=True, nullable=False,
    )
    email: Mapped[str] = mapped_column(
        String(MAX_LENGTH_EMAIL), unique=True, nullable=False,
    )
    phone: Mapped[str] = mapped_column(
        String(MAX_LENGTH_PHONE), unique=True, nullable=False,
    )
    tg_id: Mapped[str] = mapped_column(
        String(MAX_LENGTH_TG_ID), unique=True, nullable=True,
    )
    password_hash: Mapped[str] = mapped_column(
        String(MAX_LENGTH_PASS_HASH), nullable=False,
    )
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), default=UserRole.USER,
    )
    cafe_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID,
        ForeignKey('cafe.id'),
        nullable=True,
    )

    cafe: Mapped['Cafe | None'] = relationship(back_populates='managers')
    bookings: Mapped[List['Booking']] = relationship(back_populates='user')

    __table_args__ = (
        CheckConstraint(
            f"(role = '{UserRole.MANAGER.value}' AND cafe_id IS NOT NULL) OR "
            f"(role != '{UserRole.MANAGER.value}' AND cafe_id IS NULL)",
            name='check_manager_cafe')
    )

    @validates('cafe_id')
    def validate_cafe_id(
        self, key, cafe_id: uuid.UUID | None,
    ) -> uuid.UUID | None:
        """Валидация кафе для ролей пользователей."""
        if self.role == UserRole.MANAGER and cafe_id is None:
            raise ValueError('Менеджер не может быть без кафе'
                             '(cafe_id не может быть None).')

        if self.role != UserRole.MANAGER and cafe_id is not None:
            raise ValueError('Кафе может быть назначено только менеджерам'
                             '(cafe_id должно быть None).')

        return cafe_id
