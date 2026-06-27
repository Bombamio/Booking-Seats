from src.crud.table import CRUDTable
from src.models import Table


class TableService(CRUDTable):
    """Сервис для работы со столиками."""


table_service = TableService(Table)
