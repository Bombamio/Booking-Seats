"""CRUD-слой блюд.

Модуль описывает операции чтения и записи для модели `Dish`.

Классы:
   - `CRUDDish` — выборка, создание и обновление с предзагрузкой кафе.

Связанные слои:
   - бизнес-логика — в `src/services/dish.py`.
"""

from src.crud.base import CRUDBase, CRUDWithCafesMixin
from src.models import Dish


class CRUDDish(CRUDWithCafesMixin, CRUDBase):
    """CRUD функции для модели Dish."""


dish_crud = CRUDDish(Dish)
