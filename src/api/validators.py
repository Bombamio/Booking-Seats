import os
import uuid
from datetime import datetime
from http import HTTPStatus
from typing import Any, Optional

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import constants as ct
from src.crud import dish_crud
from src.models import User, UserRole


async def current_user_is_active(
    user: User,
) -> User:
    """Валидатор проверки **авторизации** пользователя."""
    if not user.is_active:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Неавторизированный пользователь',
        )
    return user


async def current_admin_or_manager(
    user: User = Depends(current_user_is_active),
) -> User:
    """Валидатор проверки прав **админа** или **менеджера**."""
    if user.role not in (UserRole.ADMIN, UserRole.MANAGER):
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Доступ запрещен',
        )
    return user


async def check_data_exists(
    crud: Any,
    session: AsyncSession,
    *filters: Any,
) -> None:
    """Универсальный валидатор проверяющий на существование данных.

    Пример:
    ```
    await vt.check_data_exists(
        dish_crud,
        session,
        Dish.id == dish_id,
    )
    ```
    """
    if not await crud.exists(session, *filters):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Данные не найдены',
        )


async def get_and_check_data_exists(
    crud: Any,
    session: AsyncSession,
    *filters: Any,
) -> Any:
    """Валидатор проверяющий на существование и возвращающий данных.

    Пример:
    ```
    dish: Dish = await vt.get_and_check_data_exists(
        dish_crud,
        session,
        Dish.id == dish_id,
    )
    ```
    """
    data = await crud.get(session, *filters)
    if data is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Данные не найдены',
        )
    return data


async def check_name_duplicate(
    name: str,
    session: AsyncSession,
    exclude_id: uuid.UUID | None = None,
) -> None:
    """Валидатор проверки на **уникальнось названия**."""
    if await dish_crud.duplicate_exists(
        name=name,
        session=session,
        exclude_id=exclude_id,
    ):
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail='Ошибка валидации данных',
        )


async def check_data_is_active(
    data: Any,
) -> None:
    """Валидатор проверки на **активность поля**."""
    if not data.is_active:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail='Ошибка валидации данных',
        )


async def check_list_data_is_active(
    list_data: Any,
) -> None:
    """Валидатор проверки списка данных на **активность поля**."""
    inactive_cafes = [data for data in list_data if not data.is_active]

    if inactive_cafes:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail='Ошибка валидации данных',
        )


async def check_cafe_managers(
    user: User,
    cafes_id: list[uuid.UUID],
    check_len: bool = False,
) -> None:
    """Проверка, что менеджер имеет доступ к кафе из списка."""
    if (check_len and len(cafes_id) != 1) or (user.cafe_id not in cafes_id):
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


async def check_slot_overlap(
    crud: Any,
    cafe_id: uuid.UUID,
    start_time: datetime,
    end_time: datetime,
    session: AsyncSession,
    exclude_id: Optional[uuid.UUID] = None,
) -> None:
    """Валидатор проверки на **пересечение временных слотов** в кафе."""
    overlapping = await crud.get_overlapping(
        cafe_id=cafe_id,
        start_time=start_time,
        end_time=end_time,
        session=session,
        exclude_id=exclude_id,
    )
    if overlapping is not None:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail='Временной слот пересекается с уже существующим',
        )


def check_belongs_to_cafe(
    data: Any,
    cafe_id: uuid.UUID,
) -> None:
    """Валидатор проверки, что объект относится к указанному кафе."""
    if data.cafe_id != cafe_id:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Данные не найдены',
        )


async def check_data_len_by_data_ids(
    data: Any,
    data_ids: Any,
) -> None:
    """Валидатор проверки количества найденных объектов, с количеством id."""
    if len(data) != len(data_ids):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Данные не найдены',
        )
