from typing import Annotated, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api import validators as validate
from crud import dishes_crud, cafe_crud
from core.db import get_session
from core.user import current_user
from schemas import dishes as schema
from models import User

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get(
    '/',
    response_model=list[schema.DishInfo],
    response_model_exclude_none=True,
)
async def get_dishes_list(
    cafe_id: Optional[int],
    user: Annotated[User, Depends(current_user)],
    session: SessionDep,
    show_active: bool = True,
):
    """
    GET `/dishes` - Получение списка блюд.
    """

    # Проверка на существование кафе.
    if cafe_id is not None:
        await validate.check_data_exists(
            crud=cafe_crud,
            data_id=cafe_id,
            session=session
        )

    result = await dishes_crud.get_by_user(
        user=user,
        cafe_id=cafe_id,
        session=session,
        show_active=show_active
    )
    return result
