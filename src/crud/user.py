from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.models import Cafe, User


class CRUDUser(CRUDBase):
    """CRUD функции для модели User."""

    async def update_link_in_cafe(
            self,
            session: AsyncSession,
            new_managers: list[User],
            new_cafe: Cafe | None,
        ) -> None:
        """Закрепляем менеджера за кафе (commit делать на стороне сервиса)."""
        for manager in new_managers:
            if new_cafe:
                manager.cafe_id = new_cafe.id
            else:
                manager.cafe_id = None
            session.add(manager)

        await session.flush()


user_crud = CRUDUser(User)
