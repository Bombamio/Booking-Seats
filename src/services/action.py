from http import HTTPStatus
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import action_crud
from src.models import User
from src.schemas import ActionCreate, ActionUpdate


class ActionService:
    """Сервис для работы с акциями."""

    def __init__(self) -> None:
        """Инициализирует сервис с CRUD-слоем акций."""
        self.crud = action_crud

    async def get_actions(
        self,
        session: AsyncSession,
        user: User,
        show_active: Optional[bool] = None,
        cafe_id=None,
    ) -> List:
        """Получить список акций с фильтрацией."""
        if user.role == user.role.USER:
            show_active = True
        return await self.crud.get_multi(
            session=session,
            active=show_active,
            cafe_id=cafe_id,
        )

    async def create_action(
        self,
        action_create: ActionCreate,
        session: AsyncSession,
    ):
        """Создать новую акцию."""
        return await self.crud.create(
            action_create=action_create,
            session=session,
        )

    async def get_action(self, action_id, session: AsyncSession, user: User):
        """Получить акцию по ID с проверкой прав доступа."""
        action = await self.crud.get(action_id, session)
        if action is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Данные не найдены',
            )
        if user.role == user.role.USER and not action.is_active:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Акция не найдена',
            )
        return action

    async def update_action(
        self,
        action_id,
        action_update: ActionUpdate,
        session: AsyncSession,
    ):
        """Обновить существующую акцию."""
        action = await self.crud.get(action_id, session)
        if action is None:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Данные не найдены',
            )
        return await self.crud.update(
            action_entity=action,
            action_update=action_update,
            session=session,
        )
