"""Сервисный слой столиков.

Модуль описывает бизнес-логику управления столиками кафе.

Классы:
   - `TableService` — список, создание, обновление и деактивация столов.

Особенности:
   - commit выполняется в методах сервиса;
   - `soft_delete` из `BaseService` меняет объекты в сессии без commit.

Связанные слои:
   - CRUD — в `src/crud/base.py`;
   - схемы — в `src/schemas/table.py`.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import CRUDBase
from src.models import Cafe, Table, User, UserRole
from src.schemas import TableCreate, TableUpdate
from src.schemas.cafe import CafeShortInfo
from src.schemas.table import TableInfo
from src.services.base import BaseService, is_active_filters


class TableService(CRUDBase, BaseService):
    """Обработает операции со столиками кафе."""

    @staticmethod
    def _to_table_info(
        table: Table,
        cafe: Cafe,
    ) -> TableInfo:
        """Соберет схему ответа стола с краткой информацией о кафе."""
        table_info = TableInfo.model_validate(table, from_attributes=True)
        table_info.cafe = CafeShortInfo.model_validate(cafe, from_attributes=True)
        return table_info

    def _apply_fields_update(
        self,
        table_entity: Table,
        table_update: TableUpdate,
    ) -> None:
        """Применит переданные поля к объекту без обращения к CRUDBase.update."""
        table_update_payload = table_update.model_dump(exclude_unset=True)
        model_fields = self.model.__table__.columns.keys()
        for field, value in table_update_payload.items():
            if field in model_fields:
                setattr(table_entity, field, value)

    async def get_multi_by_cafe(
        self,
        cafe_id: uuid.UUID,
        session: AsyncSession,
        user: User,
        show_active: bool | None = None,
    ) -> list[TableInfo]:
        """Вернёт список столиков кафе с учётом роли и ``show_active``.

        Проверяет доступ менеджера, существование кафе и собирает фильтры
        ``is_active`` по роли пользователя.
        """
        await self.ensure_manager_cafe_access(user, cafe_id)
        cafe = await self._get_cafe(session, cafe_id)

        filters = [
            self.model.cafe_id == cafe_id,
            *is_active_filters(user, show_active, self.model.is_active),
        ]

        tables = list(await self.get_multi(session, *filters))
        self.log_info(
            f'Пользователь {user.id} получил список из {len(tables)} столов для кафе {cafe_id}',
        )
        return [self._to_table_info(table, cafe) for table in tables]

    async def create_with_cafe(
        self,
        cafe_id: uuid.UUID,
        table_create: TableCreate,
        session: AsyncSession,
        user: User,
    ) -> TableInfo:
        """Создаст столик в активном кафе и вернёт ответ API.

        Проверяет существование кафе, его активность и доступ менеджера.
        Commit выполняется в этом методе.
        """
        cafe = await self._get_cafe(session, cafe_id, require_active=True)
        await self.ensure_manager_cafe_access(user, cafe.id)

        table = self.model(
            cafe_id=cafe.id,
            **table_create.model_dump(),
        )
        session.add(table)
        await session.commit()
        self.log_info(
            f'Пользователь {user.id} создал стол {table.id} в кафе {cafe_id}',
        )
        return self._to_table_info(table, cafe)

    async def get_by_cafe_and_id(
        self,
        cafe_id: uuid.UUID,
        table_id: uuid.UUID,
        session: AsyncSession,
        user: User,
    ) -> TableInfo:
        """Вернёт столик кафе по ID с проверкой принадлежности и роли.

        USER получает только активный стол.
        """
        await self.ensure_manager_cafe_access(user, cafe_id)
        cafe = await self._get_cafe(session, cafe_id)
        table = await self.get_or_raise(
            self,
            session,
            self.model.id == table_id,
        )
        self.ensure_belongs_to_cafe(table, cafe_id)

        if user.role == UserRole.USER:
            await self.ensure_is_active(table)

        self.log_info(
            f'Пользователь {user.id} получил информацию о столе {table.id} из кафе {cafe_id}',
        )
        return self._to_table_info(table, cafe)

    async def update_table(
        self,
        cafe_id: uuid.UUID,
        table_id: uuid.UUID,
        table_update: TableUpdate,
        session: AsyncSession,
        user: User,
    ) -> TableInfo:
        """Обновит информацию о столике кафе.

        При деактивации (``is_active=False``) вызовет ``soft_delete`` из
        ``BaseService``: стол и связанные ``booking_items`` получат
        ``is_active=False`` по каскаду дочерних связей.
        """
        cafe = await self._get_cafe(session, cafe_id)
        table = await self.get_or_raise(
            self,
            session,
            self.model.id == table_id,
        )
        self.ensure_belongs_to_cafe(table, cafe.id)
        await self.ensure_manager_cafe_access(user, cafe.id)

        update_data = table_update.model_dump(exclude_unset=True)
        deactivate = update_data.pop('is_active', None) is False

        if update_data:
            self._apply_fields_update(
                table,
                TableUpdate.model_validate(update_data),
            )
            session.add(table)

        if deactivate:
            table = await self.soft_delete(table, session)

        await session.commit()
        self.log_info(
            f'Пользователь {user.id} обновил стол {table_id} в кафе {cafe_id} (деактивирован: {deactivate})',
        )
        return self._to_table_info(table, cafe)


table_service = TableService(Table)
