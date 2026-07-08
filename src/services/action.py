import uuid
from typing import Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from src.core import constants as cs
from src.crud import CRUDAction, action_crud, cafe_crud
from src.models import Action, Cafe, User, UserRole
from src.schemas import ActionCreate, ActionUpdate
from src.services import BaseService


class ActionService(CRUDAction, BaseService):
    """Сервис для работы с акциями."""

    async def _ensure_description_unique(
        self,
        description: str,
        session: AsyncSession,
        exclude_id: uuid.UUID | None = None,
    ) -> None:
        """Проверит уникальность описания акции."""
        filters = [Action.description == description]
        if exclude_id is not None:
            filters.append(Action.id != exclude_id)

        if await self.exists(
            session=session,
            *filters,
        ):
            self.log_warning(f'Акция с описанием "{description[: cs.MAX_DSC_LOG_LEN]}..." - уже существует.')
            self.raise_unprocessable_entity()

    async def get_actions(
        self,
        session: AsyncSession,
        user: User,
        show_active: Optional[bool],
        cafe_id: Optional[uuid.UUID],
    ) -> Sequence[Action]:
        """Получить список акций с фильтрацией."""
        filters = []

        if cafe_id is not None:
            filters.append(Action.cafes.any(Cafe.id == cafe_id))

        if user.role == UserRole.USER or show_active or user.role == UserRole.MANAGER and show_active is None:
            filters.append(Action.is_active.is_(True))

        elif show_active is False and user.role == UserRole.MANAGER and cafe_id is not None:
            filters.append(
                Action.cafes.any(Cafe.managers.any(User.id == user.id)),
            )

        elif user.role != UserRole.USER and show_active is not None:
            filters.append(Action.is_active.is_(show_active))

        actions = await self.get_multi(session, *filters)
        self.log_info(f'Пользователь {user.id} получил список из {len(actions)} акций.')
        return actions

    async def create_action(
        self,
        action_create: ActionCreate,
        user: User,
        session: AsyncSession,
    ) -> Action:
        """Создать новую акцию."""
        cafes = await cafe_crud.get_multi(
            session,
            Cafe.id.in_(action_create.cafes_id),
        )

        await self.ensure_cafes_len(
            cafes=cafes,
            cafes_id=action_create.cafes_id,
        )
        await self.ensure_manajer_cafe_list_access(
            user=user,
            cafes_id=action_create.cafes_id,
            check_len=True,
        )
        await self._ensure_description_unique(
            description=action_create.description,
            session=session,
        )

        result = await self.create(
            action_create,
            session,
            cafes=cafes,
        )

        self.log_info(f'Пользователь {user.id} создал акцию.')

        return result

    async def get_action_by_id(
        self,
        action_id: uuid.UUID,
        session: AsyncSession,
        user: User,
    ) -> Action:
        """Получить акцию по ID с проверкой прав доступа."""
        filters = [Action.id == action_id]
        if user.role == UserRole.USER:
            filters.append(Action.is_active.is_(True))

        action: Action = await self.get_or_raise(
            action_crud,
            session,
            *filters,
        )

        await self.ensure_manajer_cafe_list_access(
            user=user,
            cafes_id=[cafe.id for cafe in action.cafes],
        )

        self.log_info(f'Пользователь {user.id} получил информацию об акции {action_id}.')

        return action

    async def update_action(
        self,
        action_id: uuid.UUID,
        action_update: ActionUpdate,
        user: User,
        session: AsyncSession,
    ) -> Action:
        """Обновить существующую акцию."""
        action: Action = await self.get_or_raise(
            action_crud,
            session,
            Action.id == action_id,
        )

        relations = {}

        if action_update.cafes_id is not None:
            cafes = await cafe_crud.get_multi(
                session,
                Cafe.id.in_(action_update.cafes_id),
            )

            await self.ensure_cafes_len(
                cafes=cafes,
                cafes_id=action_update.cafes_id,
            )

            if user.role.MANAGER:
                await self.ensure_manajer_cafe_list_access(
                    user=user,
                    cafes_id=action_update.cafes_id,
                    check_len=True,
                )

            relations['cafes'] = cafes

        if action_update.description is not None:
            await self._ensure_description_unique(
                description=action_update.description,
                session=session,
                exclude_id=action_id,
            )

        result = await self.update(
            db_entity=action,
            update_data=action_update,
            session=session,
            **relations,
        )

        self.log_info(f'Пользователь {user.id} изменил информацию об акции {action_id}.')

        return result


action_service = ActionService(Action)
