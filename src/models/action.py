import uuid
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core import constants as ct
from src.core.base_model import Base
from src.models.association_tables import cafe_actions


class Action(Base):
    """Модель Action. Онформация об акциях кафе.

    Поля:
    * `id` - uuid4, primary_key;
    * `description` - str;
    * `cafes_id` - relationship;
    * `photo` - uuid4, ForeignKey;
    * `created_at` - datetime;
    * `updated_at` - datetime;
    * `is_active` - boolean.
    """

    description: Mapped[str] = mapped_column(
        String(ct.MAX_DESCRIPTION_LEN),
        unique=True,
    )

    photo: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey('media.id', ondelete='SET NULL'),
        comment='ID медиа-файла с изображением акции',
    )

    cafes = relationship(
        'Cafe',
        secondary=cafe_actions,
        back_populates='actions',
    )

    def __repr__(self) -> str:
        return (
            f"<Action(id={self.id}, description='{self.description[:30]}...')>"
        )
