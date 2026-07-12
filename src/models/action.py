"""ORM-модель акции.

Описывает таблицу `actions` и связи акции с кафе.

Классы:
   - `Action` — акция кафе.

Связи:
   - `Action.cafes` — кафе, в которых действует акция.
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core import constants as ct
from src.core.base_model import Base
from src.models.association_tables import cafe_actions

if TYPE_CHECKING:
    from src.models import Cafe


class Action(Base):
    """ORM-модель акции кафе."""

    description: Mapped[str] = mapped_column(
        String(ct.MAX_DESCRIPTION_LEN),
        unique=True,
    )

    photo_id: Mapped[uuid.UUID | None] = mapped_column(
        comment='ID медиа-файла с изображением акции',
    )

    cafes: Mapped[list['Cafe']] = relationship(
        secondary=cafe_actions,
        back_populates='actions',
        lazy='raise',
    )

    def __repr__(self) -> str:
        """Вернёт краткое строковое представление акции."""
        return f'Action(id={self.id!r}, description={self.description!r})'
