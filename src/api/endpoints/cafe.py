from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_session

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get(
    '/',
)
async def get_cafes(
    CafeInfo,
):
    pass


@router.post(
    '/',
)
async def create_cafe():
    pass


@router.get(
    '/{cafe_id}',
)
async def get_cafes():
    pass


@router.patch(
    '/{cafe_id}',
)
async def update_cafe():
    pass
