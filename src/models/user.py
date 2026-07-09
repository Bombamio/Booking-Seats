import enum
import uuid
from typing import TYPE_CHECKING, Any, List, Optional

from sqlalchemy import CheckConstraint, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

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

    email: Mapped[Optional[str]] = mapped_column(
        String(ct.MAX_EMAIL_LEN),
        unique=True,
    )

    phone: Mapped[Optional[str]] = mapped_column(
        String(ct.MAX_PHONE_LEN),
        unique=True,
    )

    tg_id: Mapped[Optional[str]] = mapped_column(
        String(ct.MAX_TG_ID_LEN),
        unique=True,
    )

    password_hash: Mapped[str] = mapped_column(
        Text,
    )

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        default=UserRole.USER,
    )

    cafe_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey('cafes.id', ondelete='RESTRICT'),
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

    def __init__(self, **kwargs: Any) -> None:
        """Проверка после создания объекта,
        когда все поля уже существуют.
        """  # noqa: D205
        super().__init__(**kwargs)

        if self.email:
            self.email = self.email.strip()

        if self.phone:
            self.phone = self.phone.strip()

        if self.email is None and self.phone is None:
            raise ValueError(
                'Хотя бы одно из полей email/phone должно быть заполнено.',
            )

    def validate_cafe_id(self) -> None:
        """Проверка связи кафе и роли."""
        if self.role != UserRole.MANAGER and self.cafe_id is not None:
            raise ValueError(
                'Кафе может быть назначено только менеджерам.',
            )
