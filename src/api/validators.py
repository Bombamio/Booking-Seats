import os

from http import HTTPStatus

from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.user import current_user
from core import constants as ct
from models import User, Dishes


async def check_data_exists(
    crud,
    data_id: int,
    session: AsyncSession,
):
    """
    Универсальный валидатор проверяющий на **существование данных**.
    """

    data = await crud.get(data_id, session)
    if data is None:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail='Ошибка валидации данных'
        )
    return data


async def current_admin_or_manager(
    user: User = Depends(current_user)
) -> User:
    """
    Валидатор проверки прав **админа** или **менеджера**.
    """

    if not (user.role.superuser or user.role.manager):
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Доступ запрещен'
        )
    return user


async def check_name_duplicate(
    crud,
    name: str,
    cafe_id: int,
    session: AsyncSession,
) -> None:
    """
    Валидатор проверки на **уникальнось названия**.
    """

    result = await crud.get_by_name(
        cafe_id=cafe_id,
        name=name,
        session=session
    )

    if result is not None:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail='Ошибка валидации данных'
        )


async def check_data_is_active(
    crud,
    data_id: int,
    session: AsyncSession,
) -> None:
    """
    Валидатор проверки на **активность поля**.
    """
    data = await crud.get(
        obj_id=data_id,
        session=session
    )

    if data.active is False:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Данные не найдены'
        )


async def check_cafe_managers(
    crud,
    user: User,
    cafe_id: int,
    session: AsyncSession
) -> None:
    """
    Валидатор проверки на **роль менеджера** определённого кафе.
    """

    managers = await crud.get_managers_by_cafe(
        cafe_id=cafe_id,
        session=session
    )
    if user.id not in managers:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Доступ запрещен'
        )


async def check_cafe_manager_by_dish(
    crud,
    user: User,
    dish: Dishes,
    session: AsyncSession
) -> None:
    """
    Валидатор проверки на **роль менеджера** кафе c определённым блюдом.
    """

    cafes_id = await crud.get_cafes_by_manager(
        manager_id=user.id,
        session=session
    )
    # Проверяет вхождение кафе менеджера в список кафе, в которых есть блюдо.
    if not any(cafe.id in cafes_id for cafe in dish.cafes):
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Доступ запрещен'
        )


async def get_size(
    file_id
) -> None:
    """
    Валидатор проверки размера файла.
    """

    # Скорее всего неправильно написал.
    if os.path.getsize(file_id) > ct.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail='Ошибка валидации данных'
        )
