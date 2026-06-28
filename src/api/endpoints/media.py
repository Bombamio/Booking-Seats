import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Response, UploadFile, status

from src.api import validators as vt
from src.core.constants import (
    ERRORS_GET_MEDIA,
    ERRORS_POST_MEDIA,
    MEDIA_OUTPUT_TYPE,
)
from src.core.decorators import with_error_responses
from src.models import User
from src.schemas import media as schema
from src.services.media import media_service

router = APIRouter()


@router.post(
    '/',
    response_model=schema.MediaInfo,
    status_code=status.HTTP_201_CREATED,
    summary='Загрузка изображения',
    description=(
        'Загрузка изображения на сервер. '
        'Поддерживаются форматы jpg, png. '
        'Размер файла не более 5 Мб. '
        'Только для администраторов и менеджеров.'
    ),
)
@with_error_responses(ERRORS_POST_MEDIA)
async def upload_media(
    user: Annotated[User, Depends(vt.current_admin_or_manager)],
    file: Annotated[UploadFile],
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
    responses={
        status.HTTP_200_OK: {
            'content': {
                'image/jpeg': {},
            },
            'description': 'Возвращает изображение в бинарном формате',
        },
    },
)
@with_error_responses(ERRORS_GET_MEDIA)
async def get_media(
    media_id: uuid.UUID,
) -> Response:
    """Получение изображения по ID."""
    content = await media_service.get_image(media_id)
    return Response(content=content, media_type=MEDIA_OUTPUT_TYPE)
