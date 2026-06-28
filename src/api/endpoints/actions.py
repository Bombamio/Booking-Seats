from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.validators import current_user, current_admin_or_manager
from src.core.db import get_db
from src.crud.action import CRUDAction
from src.models.user import User
from src.schemas.action import ActionCreate, ActionInfo, ActionUpdate
from src.services.action import ActionService

router = APIRouter(prefix='/actions', tags=['Акции'])

crud_action = CRUDAction()
action_service = ActionService(crud_action)


@router.get('/', response_model=List[ActionInfo])
async def get_actions(
    show_active: Optional[bool] = Query(None),
    cafe_id: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    return await action_service.get_actions(
        session=session, user=user,
        show_active=show_active, cafe_id=cafe_id,
    )


@router.post(
        '/', response_model=ActionInfo, status_code=status.HTTP_201_CREATED
)
async def create_action(
    action_in: ActionCreate,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(current_admin_or_manager),
):
    return await action_service.create_action(
        obj_in=action_in, session=session
    )


@router.get('/{action_id}', response_model=ActionInfo)
async def get_action(
    action_id,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(current_user),
):
    return await action_service.get_action(
        action_id=action_id, session=session, user=user,
    )


@router.patch('/{action_id}', response_model=ActionInfo)
async def update_action(
    action_id,
    action_in: ActionUpdate,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(current_admin_or_manager),
):
    return await action_service.update_action(
        action_id=action_id, obj_in=action_in, session=session,
    )
