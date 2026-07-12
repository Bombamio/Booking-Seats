"""Сервисный слой акций.

Модуль описывает бизнес-логику управления акциями кафе.

Классы:
   - `ActionService` — список, создание, получение и обновление акций.

Связанные слои:
   - CRUD — в `src/crud/action.py`;
   - схемы — в `src/schemas/action.py`.
"""

import uuid
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from src.core import constants as cs
from src.crud import CRUDAction, action_crud
from src.models import Action, User, UserRole
from src.schemas import ActionCreate, ActionUpdate
from src.services.base import BaseService


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

        if await self.exists(session, *filters):
            self.log_warning(f'Акция с описанием "{description[: cs.MAX_DSC_LOG_LEN]}..." - уже существует.')
            self.raise_unprocessable_entity()

    async def get_actions(
        self,
        session: AsyncSession,
        user: User,
        show_active: bool | None,
        cafe_id: uuid.UUID | None,
    ) -> Sequence[Action]:
        """Вернёт список акций с фильтрацией по кафе и ``show_active``.

        Логика фильтрации ``is_active`` совпадает с блюдами и другими сущностями
        через ``is_active_filters``.
        """
        filters = await self._filters_for_cafe_linked_entity(
            session=session,
            user=user,
            show_active=show_active,
            cafe_id=cafe_id,
            entity_model=Action,
            is_active_column=Action.is_active,
        )

        actions = await self.get_multi(session, *filters)
        self.log_info(f'Пользователь {user.id} получил список из {len(actions)} акций.')
        return actions

    async def create_action(
        self,
        action_create: ActionCreate,
        user: User,
        session: AsyncSession,
    ) -> Action:
        """Создаст акцию и привяжет её к кафе из ``cafes_id``.

        Проверяет существование кафе, доступ менеджера и уникальность описания.
        """
        cafes = await self._load_cafes_for_link(
            session,
            action_create.cafes_id,
            user,
            check_manager_single=True,
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
        """Вернёт акцию по ID с проверкой роли и доступа менеджера к её кафе."""
        filters = [Action.id == action_id]
        if user.role == UserRole.USER:
            filters.append(Action.is_active.is_(True))

        action: Action = await self.get_or_raise(
            action_crud,
            session,
            *filters,
        )

        await self.ensure_manager_cafe_list_access(
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
        """Обновит акцию: поля, привязку к кафе и описание.

        При смене ``cafes_id`` проверяет существование кафе и доступ менеджера.
        При смене ``description`` проверяет уникальность среди других акций.
        """
        action: Action = await self.get_or_raise(
            action_crud,
            session,
            Action.id == action_id,
        )

        relations = {}

        if action_update.cafes_id is not None:
            relations['cafes'] = await self._load_cafes_for_link(
                session,
                action_update.cafes_id,
                user,
                check_manager_single=True,
            )

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
