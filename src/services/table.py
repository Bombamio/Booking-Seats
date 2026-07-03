import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import CRUDTable, cafe_crud
from src.models import Cafe, Table, User, UserRole
from src.schemas import TableCreate, TableUpdate
from src.services.base import BaseService


# Допущения до рефакторинга базовых слоёв:
# - CRUDBase выполняет только чтение/подготовку данных без commit и refresh;
# - фиксация изменений в БД (commit) выполняется в методах сервиса;
# - soft_delete из BaseService также не делает commit — только меняет
# объекты в сессии.
class TableService(CRUDTable, BaseService):
    """Обработает операции со столиками кафе."""

    async def ensure_manager_cafe_access(
        self,
        user: User,
        cafe_id: uuid.UUID,
        session: AsyncSession,
    ) -> None:
        """Проверит, что менеджер привязан к указанному кафе."""
        if user.role != UserRole.MANAGER:
            return
        if user.cafe_id is None or user.cafe_id != cafe_id:
            self.log_warning(
                f'Пользователь {user.id} попытался получить доступ к'
                f'кафе {cafe_id} без разрешения',
            )
            self.raise_forbidden('Доступ запрещен')

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
        show_active: bool = True,
    ) -> list[Table]:
        """Вернет список столиков кафе с учётом роли пользователя.

        Пользователь всегда получит только активные столы.
        Администратор и менеджер при ``show_active=True`` — только активные,
        при ``show_active=False`` — все столы кафе.
        """
        await self.ensure_manager_cafe_access(user, cafe_id, session)
        await self.ensure_exists(
            cafe_crud,
            session,
            Cafe.id == cafe_id,
        )

        filters = [self.model.cafe_id == cafe_id]
        if user.role == UserRole.USER or show_active:
            filters.append(self.model.is_active.is_(True))

        tables = list(await self.get_multi(session, *filters))
        self.log_info(
            f'Пользователь {user.id} получил список из {len(tables)}'
            f'столов для кафе {cafe_id}',
        )
        return tables

    async def create_with_cafe(
        self,
        cafe_id: uuid.UUID,
        table_create: TableCreate,
        session: AsyncSession,
        user: User,
    ) -> Table:
        """Создаст столик, привязанный к указанному кафе."""
        cafe = await self.get_or_raise(
            cafe_crud,
            session,
            Cafe.id == cafe_id,
        )
        await self.ensure_is_active(cafe)
        await self.ensure_manager_cafe_access(user, cafe.id, session)

        table = self.model(
            cafe_id=cafe.id,
            **table_create.model_dump(),
        )
        session.add(table)
        await session.commit()
        self.log_info(
            f'Пользователь {user.id} создал стол {table.id} в кафе {cafe_id}',
        )
        return table

    async def get_by_cafe_and_id(
        self,
        cafe_id: uuid.UUID,
        table_id: uuid.UUID,
        session: AsyncSession,
        user: User,
    ) -> Table:
        """Вернет столик кафе по его ID."""
        await self.ensure_manager_cafe_access(user, cafe_id, session)
        await self.ensure_exists(
            cafe_crud,
            session,
            Cafe.id == cafe_id,
        )
        table = await self.get_or_raise(
            self,
            session,
            self.model.id == table_id,
        )
        self.ensure_belongs_to_cafe(table, cafe_id)

        if user.role == UserRole.USER:
            await self.ensure_is_active(table)

        self.log_info(
            f'Пользователь {user.id} получил информацию о столе {table.id}'
            f'из кафе {cafe_id}',
        )
        return table

    async def update_table(
        self,
        cafe_id: uuid.UUID,
        table_id: uuid.UUID,
        table_update: TableUpdate,
        session: AsyncSession,
        user: User,
    ) -> Table:
        """Обновит информацию о столике кафе.

        При деактивации (``is_active=False``) вызовет ``soft_delete`` из
        ``BaseService``: стол и связанные ``booking_items`` получат
        ``is_active=False`` по каскаду дочерних связей.
        """
        cafe = await self.get_or_raise(
            cafe_crud,
            session,
            Cafe.id == cafe_id,
        )
        table = await self.get_or_raise(
            self,
            session,
            self.model.id == table_id,
        )
        self.ensure_belongs_to_cafe(table, cafe.id)
        await self.ensure_manager_cafe_access(user, cafe.id, session)

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
            f'Пользователь {user.id} обновил стол {table_id} в'
            f'кафе {cafe_id} (деактивирован: {deactivate})',
        )
        return table


table_service = TableService(Table)
