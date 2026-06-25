import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api import validators as vt
from src.core.db import get_session
from src.crud import cafe_crud, dish_crud
from src.models import User
from src.schemas import dish as schema
from src.core.cache import cache


router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get(
    '/',
    response_model=list[schema.DishInfo],
    response_model_exclude_none=True,
)
async def get_dishes_list(  # noqa: ANN201
    cafe_id: Optional[uuid.UUID],
    user: Annotated[User, Depends(vt.current_user)],
    session: SessionDep,
    show_active: bool = True,
):
    """GET `/dishes` - Получение списка блюд."""
    if cafe_id is not None:
        await vt.check_data_exists(
            crud=cafe_crud,
            data_id=cafe_id,
            session=session,
        )

    return await dish_crud.get_list_by_user(
        user=user,
        cafe_id=cafe_id,
        session=session,
        show_active=show_active,
    )


@router.post(
    '/',
    response_model=[schema.DishInfo],
    response_model_exclude_none=True,
)
async def create_dishes(  # noqa: ANN201
    obj_in: schema.DishCreate,
    user: Annotated[User, Depends(vt.current_admin_or_manager)],
    session: SessionDep,
):
    """POST `/dishes` - Создает новое блюда."""
    if obj_in.photo_id is not None:
        await vt.get_size(obj_in.photo_id)

    for cafe_id in obj_in.cafes_id:
        cafe = await vt.check_data_exists(
            crud=cafe_crud,
            data_id=cafe_id,
            session=session,
        )
        await vt.check_data_is_active(
            crud=cafe_crud,
            data_id=cafe.id,
            session=session,
        )
        await vt.check_name_duplicate(
            crud=dish_crud,
            name=obj_in.name,
            cafe_id=cafe.id,
            session=session,
        )
        await vt.check_cafe_managers(
            crud=cafe_crud,
            user=user,
            cafe_id=cafe.id,
            session=session,
        )

    result = await dish_crud.create(obj_in, session)

    await cache.clear_pattern("dishes:cafe:*")

    return result


@router.get(
    '/{dish_id}',
    response_model=schema.DishInfo,
    response_model_exclude_none=True,
)
async def get_dish_by_id(  # noqa: ANN201
    dish_id: uuid.UUID,
    user: Annotated[User, Depends(vt.current_user)],
    session: SessionDep,
):
    """GET `/dishes/{dish_id}` - Получение информации о блюде по его ID."""
    dish = await vt.check_data_exists(
        crud=dish_crud,
        data_id=dish_id,
        session=session,
    )
    # Если обычный залогиненый пользователь - проверит блюдо на активность.
    if not user.role.ADMIN and not user.role.MANAGER:
        await vt.check_data_is_active(
            crud=dish_crud,
            data_id=dish.id,
            session=session,
        )
    elif user.role.MANAGER:
        await vt.check_cafe_manager_by_dish(
            crud=cafe_crud,
            user=user,
            dish=dish,
            session=session,
        )

    return await dish_crud.get_by_user(
        user=user,
        dish=dish,
        session=session,
    )


@router.patch(
    '/{dish_id}',
    response_model=schema.DishInfo,
    response_model_exclude_none=True,
)
async def update_dishe(  # noqa: ANN201
    dish_id: uuid.UUID,
    obj_in: schema.DishUpdate,
    user: Annotated[User, Depends(vt.current_admin_or_manager)],
    session: SessionDep,
):
    """PATCH `/dishes/{dish_id}` - обновление информации о блюде по его ID."""
    if obj_in.photo_id is not None:
        await vt.get_size(obj_in.photo_id)

    dish = await vt.check_data_exists(
        crud=dish_crud,
        data_id=dish_id,
        session=session,
    )

    if obj_in.cafes_id is not None:
        for cafe_id in obj_in.cafes_id:
            # Неуверен что эта проверка нужна, но пусть будет.
            cafe = await vt.check_data_exists(
                crud=cafe_crud,
                data_id=cafe_id,
                session=session,
            )

            if user.role.MANAGER:
                await vt.check_cafe_managers(
                    crud=cafe_crud,
                    user=user,
                    cafe_id=cafe.id,
                    session=session,
                )

            if obj_in.name is not None:
                await vt.check_name_duplicate(
                    crud=dish_crud,
                    name=obj_in.name,
                    cafe_id=cafe.id,
                    session=session,
                )

    result = await dish_crud.update(
        db_obj=dish,
        obj_in=obj_in,
        session=session,
    )

    await cache.clear_pattern("dishes:cafe:*")

    return result
