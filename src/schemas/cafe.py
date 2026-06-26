from src.schemas import BaseProjectCreate, BaseProjectShortInfo


class CafeCreate(BaseProjectCreate):
    name: str
    address: str
    phone: str
    photo_id: UUID
    managers_id: list


class CafeInfo(BaseProjectShortInfo):
    pass


class CafeShortInfo(BaseProjectShortInfo):
    pass


class CafeUpdate(BaseProjectShortInfo):
    pass
