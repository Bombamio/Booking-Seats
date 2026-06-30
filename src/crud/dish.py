from src.crud.base import CRUDBase
from src.models import Dish


class CRUDDish(CRUDBase):
    """CRUD функции для модели Dish."""


dish_crud = CRUDDish(Dish)
