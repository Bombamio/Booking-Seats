import os
import uuid
from http import HTTPStatus

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.validators import current_user
from src.core import constants as ct
from src.models import Dish, User


async def check_data_exists(  # noqa: ANN201
    crud,  # noqa: ANN001
    data_id: uuid.UUID,
    session: AsyncSession,
):
    """Универсальный валидатор проверяющий на существование данных."""
    data = await crud.get(data_id, session)
    if data is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Данные не найдены',
        )
    return data


async def current_admin_or_manager(
    user: User = Depends(current_user),
) -> User:
    """Валидатор проверки прав **админа** или **менеджера**."""
    if not (user.role.ADMIN or user.role.MANAGER):
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Доступ запрещен',
        )
    return user


async def current_user(
    user: User = Depends(current_user),
) -> User:
    """Валидатор проверки **авторизации** пользователя."""
    if not (user.role.ADMIN or user.role.MANAGER or user.role.USER):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Неавторизированный пользователь',
        )
    return user


async def check_name_duplicate(
    crud,  # noqa: ANN001
    name: str,
    cafe_id: uuid.UUID,
    session: AsyncSession,
) -> None:
    """Валидатор проверки на **уникальнось названия**."""
    result = await crud.get_by_name(
        cafe_id=cafe_id,
        name=name,
        session=session,
    )

    if result is not None:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail='Ошибка валидации данных',
        )


async def check_data_is_active(
    crud,  # noqa: ANN001
    data_id: uuid.UUID,
    session: AsyncSession,
) -> None:
    """Валидатор проверки на **активность поля**."""
    data = await crud.get(
        obj_id=data_id,
        session=session,
    )

    if data.active is False:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Данные не найдены',
        )


async def check_cafe_managers(
    crud,  # noqa: ANN001
    user: User,
    cafe_id: uuid.UUID,
    session: AsyncSession,
) -> None:
    """Валидатор проверки на **роль менеджера** определённого кафе."""
    managers = await crud.get_managers_by_cafe(
        cafe_id=cafe_id,
        session=session,
    )
    if user.id not in managers:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Доступ запрещен',
        )


async def check_cafe_manager_by_dish(
    crud,  # noqa: ANN001
    user: User,
    dish: Dish,
    session: AsyncSession,
) -> None:
    """Валидатор проверки на **роль менеджера** кафе c определённым блюдом."""
    cafes_id = await crud.get_cafes_by_manager(
        manager_id=user.id,
        session=session,
    )
    # Проверяет вхождение кафе менеджера в список кафе, в которых есть блюдо.
    if not any(cafe.id in cafes_id for cafe in dish.cafes):
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Доступ запрещен',
        )


async def get_size(
    file_id: uuid.UUID,
) -> None:
    """Валидатор проверки размера файла."""
    # TODO: Скорее всего неправильно написал. Просто пример.
    if os.path.getsize(file_id) > ct.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail='Ошибка валидации данных',
        )
