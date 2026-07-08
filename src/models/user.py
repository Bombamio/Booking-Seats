import enum
import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import CheckConstraint, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from src.core import constants as ct
from src.core.base_model import Base

if TYPE_CHECKING:
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
        nullable=True,
    )
    phone: Mapped[str] = mapped_column(
        String(ct.MAX_PHONE_LEN),
        unique=True,
        nullable=True,
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
        ForeignKey('cafes.id', ondelete='RESTRICT'),
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
            f"(role = '{UserRole.MANAGER.value}' OR cafe_id IS NULL)",
            name='check_manager_cafe',
        ),
        CheckConstraint(
            'email IS NOT NULL OR phone IS NOT NULL',
            name='check_contact_info',
        ),
    )

    @validates('email', 'phone')
    def validate_contact_info(
        self,
        key: str,
        value: str | None,
    ) -> str | None:
        """Валидация: хотя бы одно из полей email/phone заполнено."""
        if key == 'email':
            email = value.strip() if isinstance(value, str) else None
        elif key == 'phone':
            phone = value.strip() if isinstance(value, str) else None

        if email is None and phone is None:
            raise ValueError('Хотя бы одно из полей email/phone должно быть заполнено.')

        return value

    @validates('cafe_id')
    def validate_cafe_id(
        self,
        key: str,
        cafe_id: uuid.UUID | None,
    ) -> uuid.UUID | None:
        """Валидация кафе для роли пользователя: менеджер."""
        if self.role == UserRole.MANAGER or cafe_id is None:
            return cafe_id

        raise ValueError('Кафе может быть назначено только менеджерам (cafe_id должно быть None).')
