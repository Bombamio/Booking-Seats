import enum
import uuid
from typing import List, Optional

from sqlalchemy import CheckConstraint, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from src.core import constants as ct
from src.core.base_model import Base
from src.models import Booking, Cafe


class UserRole(enum.Enum):
    """Роли пользователей."""

    ADMIN = 'ADMIN'
    MANAGER = 'MANAGER'
    USER = 'USER'


class User(Base):
    """Модель пользователя."""

    username: Mapped[str] = mapped_column(
        String(ct.MAX_USERNAME_LEN),
        unique=True,
    )
    email: Mapped[str] = mapped_column(
        String(ct.MAX_EMAIL_LEN),
        unique=True,
    )
    phone: Mapped[str] = mapped_column(
        String(ct.MAX_PHONE_LEN),
        unique=True,
    )
    tg_id: Mapped[Optional[str]] = mapped_column(
        String(ct.MAX_TG_ID_LEN),
        unique=True,
    )
    password_hash: Mapped[str] = mapped_column(
        String(ct.MAX_PASS_HASH_LEN),
    )
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        default=UserRole.USER,
    )
    cafe_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey('cafe.id'),
        nullable=True,
    )

    cafe: Mapped['Cafe | None'] = relationship(
        back_populates='managers',
    )
    bookings: Mapped[List['Booking']] = relationship(
        back_populates='user',
    )

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
