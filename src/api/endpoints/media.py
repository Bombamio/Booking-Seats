"""Эндпоинты медиафайлов.

Модуль описывает маршруты загрузки и выдачи изображений.

Маршруты:
   - `POST /` — загрузка изображения;
   - `GET /{media_id}` — получение изображения по ID.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Response, UploadFile, status

from src.api import error_responses as er
from src.api import validators as vt
from src.api.openapi_examples import SUCCESS_MEDIA_IMAGE, SUCCESS_MEDIA_INFO, merge_responses
from src.core.constants import MEDIA_OUTPUT_TYPE
from src.models import User
from src.schemas import media as schema
from src.services import media_service

router = APIRouter()


@router.post(
    '/',
    response_model=schema.MediaInfo,
    status_code=status.HTTP_201_CREATED,
    summary='Загрузка изображения',
    responses=merge_responses(SUCCESS_MEDIA_INFO, er.ERRORS_POST_MEDIA),
    description=(
        'Загрузка изображения на сервер. '
        'Поддерживаются форматы jpg, png. '
        'Размер файла не более 5 Мб. '
        'Только для администраторов и менеджеров.'
    ),
)
async def upload_media(
    user: Annotated[User, Depends(vt.current_admin_or_manager)],
    file: UploadFile,
) -> schema.MediaInfo:
    """Загрузка изображения."""
    return await media_service.upload(
        file=file,
        user=user,
    )


@router.get(
    '/{media_id}',
    summary='Получение изображения',
    description='Вернет изображение в бинарном формате по его ID.',
    responses=merge_responses(SUCCESS_MEDIA_IMAGE, er.ERRORS_GET_MEDIA),
)
async def get_media(
    media_id: uuid.UUID,
) -> Response:
    """Получение изображения по ID."""
    content = await media_service.get_image(media_id)
    return Response(content=content, media_type=MEDIA_OUTPUT_TYPE)
