from typing import Annotated, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api import validators as vt
from crud import dishes_crud, cafes_crud
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

    if cafe_id is not None:
        await vt.check_data_exists(
            crud=cafes_crud,
            data_id=cafe_id,
            session=session
        )

    result = await dishes_crud.get_list_by_user(
        user=user,
        cafe_id=cafe_id,
        session=session,
        show_active=show_active
    )
    return result


@router.post(
    '/',
    response_model=[schema.DishInfo],
    response_model_exclude_none=True,
)
async def create_dishes(
    obj_in: schema.DishCreate,
    user: Annotated[User, Depends(vt.current_admin_or_manager)],
    session: SessionDep,
):
    """
    POST `/dishes` - Создает новое блюда.
    """

    if obj_in.photo_id is not None:
        await vt.get_size(obj_in.photo_id)

    for cafe_id in obj_in.cafes_id:
        cafe = await vt.check_data_exists(
            crud=cafes_crud,
            data_id=cafe_id,
            session=session
        )
        await vt.check_data_is_active(
            crud=cafes_crud,
            data_id=cafe.id,
            session=session
        )
        await vt.check_name_duplicate(
            crud=dishes_crud,
            name=obj_in.name,
            cafe_id=cafe.id,
            session=session
        )
        await vt.check_cafe_managers(
            crud=cafes_crud,
            user=user,
            cafe_id=cafe.id,
            session=session
        )

    result = await dishes_crud.create(obj_in, session)
    return result


@router.get(
    '/{dish_id}',
    response_model=schema.DishInfo,
    response_model_exclude_none=True,
)
async def get_dish_by_id(
    dish_id: int,
    user: Annotated[User, Depends(current_user)],
    session: SessionDep,
):
    """
    GET `/dishes/{dish_id}` - Получение информации о блюде по его ID.
    """

    dish = await vt.check_data_exists(
        crud=dishes_crud,
        data_id=dish_id,
        session=session
    )
    # Если обычный залогиненый пользователь - проверит блюдо на активность.
    if not user.role.superuser and not user.role.manager:
        await vt.check_data_is_active(
            crud=dishes_crud,
            data_id=dish.id,
            session=session
        )
    elif user.role.manager:
        await vt.check_cafe_manager_by_dish(
            crud=cafes_crud,
            user=user,
            dish=dish,
            session=session
        )

    result = await dishes_crud.get_by_user(
        user=user,
        dish=dish,
        session=session,
    )
    return result


@router.patch(
    '/{dish_id}',
    response_model=schema.DishInfo,
    response_model_exclude_none=True,
)
async def update_dishe(
    dish_id: int,
    obj_in: schema.DishUpdate,
    user: Annotated[User, Depends(vt.current_admin_or_manager)],
    session: SessionDep,
):
    """
    PATCH `/dishes/{dish_id}` - обновление информации о блюде по его ID.
    """

    if obj_in.photo_id is not None:
        await vt.get_size(obj_in.photo_id)

    dish = await vt.check_data_exists(
        crud=dishes_crud,
        data_id=dish_id,
        session=session
    )

    if obj_in.cafes_id is not None:
        for cafe_id in obj_in.cafes_id:
            # Неуверен что эта проверка нужна, но пусть будет.
            cafe = await vt.check_data_exists(
                crud=cafes_crud,
                data_id=cafe_id,
                session=session
            )

            if user.role.manager:
                await vt.check_cafe_managers(
                    crud=cafes_crud,
                    user=user,
                    cafe_id=cafe.id,
                    session=session
                )

            if obj_in.name is not None:
                await vt.check_name_duplicate(
                    crud=dishes_crud,
                    name=obj_in.name,
                    cafe_id=cafe.id,
                    session=session
                )

    result = await dishes_crud.update(
        db_obj=dish,
        obj_in=obj_in,
        session=session
    )
    return result
