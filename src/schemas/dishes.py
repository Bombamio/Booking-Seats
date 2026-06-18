from datetime import datetime
from typing import Optional

from pydantic import Field, ConfigDict

from schemas.base import BaseProjectModel, BaseProjectDB
from core import constants as cs


class DishCreate(BaseProjectModel):
    name: str = Field(
        ...,
        max_length=cs.DISHES_MAX_NAME_LEN,
        min_length=cs.DISHES_MIN_NAME_LEN
    )
    description: Optional[str] = Field(
        None,
        min_length=cs.DISHES_MIN_DESC_LEN
    )
    photo_id: number
    price: 
    cafes_id: int = Field(...)


class DishInfo():
    pass


class DishUpdate():
    pass
