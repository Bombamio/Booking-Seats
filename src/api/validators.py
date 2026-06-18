from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


async def check_data_exists(
        crud,
        data_id: int,
        session: AsyncSession,
):
    """
    Универсальный валидатор проверяющий на существование данных.
    """

    data = await crud.get(data_id, session)
    if data is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Данные не найдены'
        )
    return data
