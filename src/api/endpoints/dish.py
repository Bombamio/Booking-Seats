import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api import validators as vt
from src.core import constants as cs
from src.core.db import get_session
from src.core.decorators import with_error_responses
from src.models import Dish, User
from src.schemas import dish as schema
from src.services import dish_service

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get(
    '/',
    response_model=list[schema.DishInfo],
)
@with_error_responses(cs.ERRORS_GET_MULTI_WITH_404)
async def get_multi(
    cafe_id: Optional[uuid.UUID],
    user: Annotated[User, Depends(vt.current_user)],
    session: SessionDep,
    show_active: Optional[bool],
) -> list[Optional[Dish]]:
    """GET `/dishes` - Получение списка блюд."""
    """ Старая версия.
    filters = []

    if cafe_id is not None:
        filters.append(Dish.cafes.any(Cafe.id == cafe_id))

    if user.role == UserRole.ADMIN:
        if show_active is not None:
            filters.append(Dish.is_active.is_(show_active))
    elif user.role == UserRole.MANAGER:
        filters.append(
            Dish.cafes.any(Cafe.managers.any(User.id == user.id)),
        )
        filters.append(Dish.is_active.is_(show_active))
    else:
        filters.append(Dish.is_active.is_(True))

    return list(await dish_crud.get_multi(
        session,
        *filters,
    ))
    """

    return await dish_service.get_multi_dishes(
        cafe_id=cafe_id,
        user=user,
        session=session,
        show_active=show_active,
    )


@router.post(
    '/',
    response_model=[schema.DishInfo],
)
async def create(
    obj_in: schema.DishCreate,
    user: Annotated[User, Depends(vt.current_admin_or_manager)],
    session: SessionDep,
) -> Dish:
    """POST `/dishes` - Создает новое блюда."""
    """ Старая версия.
    cafes = await cafe_crud.get_multi(
        session,
        Cafe.id.in_(obj_in.cafes_id),
    )
    await vt.check_data_len_by_data_ids(
        data=cafes,
        data_ids=obj_in.cafes_id,
    )

    if user.role.MANAGER:
        await vt.check_cafe_managers(
            user=user,
            cafes_id=obj_in.cafes_id,
            check_len=True,
        )
    await vt.check_name_duplicate(
        name=obj_in.name,
        session=session,
    )

    result = await dish_crud.create(
        obj_in,
        session,
        cafes=cafes,
    )

    await cache.clear_pattern("dishes:cafe:*")

    return result
    """

    return await dish_service.create_dish(
        obj_in=obj_in,
        user=user,
        session=session,
    )


@router.get(
    '/{dish_id}',
    response_model=schema.DishInfo,
)
async def get_by_id(
    dish_id: uuid.UUID,
    user: Annotated[User, Depends(vt.current_user)],
    session: SessionDep,
) -> Dish:
    """GET `/dishes/{dish_id}` - Получение информации о блюде по его ID."""
    """ Старая версия.
    filters = [Dish.id == dish_id]
    if user.role == UserRole.USER:
        filters.append(Dish.is_active.is_(True))

    dish: Dish = await vt.get_and_check_data_exists(
        dish_crud,
        session,
        *filters,
    )

    if user.role == UserRole.MANAGER:
        await vt.check_cafe_managers(
            user=user,
            cafes_id=[cafe.id for cafe in dish.cafes],
        )

    return dish
    """

    return await dish_service.get_dish_by_id(
        dish_id=dish_id,
        user=user,
        session=session,
    )


@router.patch(
    '/{dish_id}',
    response_model=schema.DishInfo,
)
async def update(
    dish_id: uuid.UUID,
    obj_in: schema.DishUpdate,
    user: Annotated[User, Depends(vt.current_admin_or_manager)],
    session: SessionDep,
) -> Dish:
    """PATCH `/dishes/{dish_id}` - обновление информации о блюде по его ID."""
    """
    dish: Dish = await vt.get_and_check_data_exists(
        dish_crud,
        session,
        Dish.id == dish_id,
    )

    relations = {}

    if obj_in.cafes_id is not None:
        if user.role.MANAGER:
            await vt.check_cafe_managers(
                user=user,
                cafes_id=obj_in.cafes_id,
                check_len=True,
            )

        cafes = await cafe_crud.get_multi(
            session,
            Cafe.id.in_(obj_in.cafes_id),
        )
        relations['cafes'] = cafes

    if obj_in.name is not None:
        await vt.check_name_duplicate(
            name=obj_in.name,
            session=session,
            exclude_id=dish.id,
        )

    result = await dish_crud.update(
        db_obj=dish,
        obj_in=obj_in,
        session=session,
        **relations,
    )

    await cache.clear_pattern("dishes:cafe:*")

    return result
    """
    return await dish_service.update_dish(
        dish_id=dish_id,
        obj_in=obj_in,
        user=user,
        session=session,
    )
