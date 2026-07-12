"""CRUD-слой акций.

Модуль описывает операции чтения и записи для модели `Action`.

Классы:
   - `CRUDAction` — выборка, создание и обновление с предзагрузкой кафе.

Связанные слои:
   - бизнес-логика — в `src/services/action.py`.
"""

from src.crud.base import CRUDBase, CRUDWithCafesMixin
from src.models import Action


class CRUDAction(CRUDWithCafesMixin, CRUDBase):
    """CRUD функции для модели Action."""


action_crud = CRUDAction(Action)
