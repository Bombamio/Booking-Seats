import asyncio
import uuid
from io import BytesIO
from pathlib import Path

from PIL import Image, UnidentifiedImageError
from fastapi import UploadFile, status

from src.core import constants as ct
from src.core.exceptions import BookingSeatsAppError
from src.models import User
from src.schemas.media import MediaInfo
from src.services.base import BaseService


class MediaService(BaseService):
    """Обработает операции с изображениями."""

    def _get_media_path(self, media_id: uuid.UUID) -> Path:
        """Вернет путь к файлу изображения на диске."""
        return ct.MEDIA_DIR / f'{media_id}{ct.MEDIA_FILE_EXTENSION}'

    def _convert_to_jpg(self, content: bytes) -> bytes:
        """Конвертирует изображение в формат JPG."""
        with Image.open(BytesIO(content)) as image:
            #  у png есть прозрачность, у jpg нет. Меняем прозрачность на белый.
            if image.mode in ('RGBA', 'LA'):
                rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                rgb_image.paste(image, mask=image.split()[-1])
                image = rgb_image
            else:
                image = image.convert('RGB')

            buffer = BytesIO()
            image.save(buffer, format='JPEG')
            return buffer.getvalue()

    async def _read_upload_file(
        self,
        file: UploadFile,
        user: User,
    ) -> bytes:
        """Считает загружаемый файл и сначала проверит сигнатуру."""
        #  закрывает файл после чтения даже при досрочном выходе из контекста
        async with file:
            content = bytearray()

            first_chunk = await file.read(ct.MEDIA_SIGNATURE_CHECK_SIZE)
            if not first_chunk:
                raise BookingSeatsAppError(
                    status.HTTP_422_UNPROCESSABLE_ENTITY,
                    'Файл не передан',
                )

            self._detect_image_type(first_chunk)
            content.extend(first_chunk)
            total_size = len(first_chunk)

            while chunk := await file.read(ct.MEDIA_CHUNK_SIZE):
                total_size += len(chunk)
                if total_size > ct.MAX_FILE_SIZE:
                    self.log_warning(
                        f'Пользователь {user.id} попытался загрузить файл, '
                        f'превышающий допустимый размер',
                    )
                    raise BookingSeatsAppError(
                        status.HTTP_422_UNPROCESSABLE_ENTITY,
                        'Размер файла превышает допустимый',
                    )
                content.extend(chunk)

            return bytes(content)

    def _detect_image_type(self, content: bytes) -> str:
        """Определит тип изображения по сигнатуре файла."""
        for signature, media_type in ct.MEDIA_IMAGE_SIGNATURES.items():
            if content.startswith(signature):
                return media_type
        formats = ', '.join(ct.ALLOWED_MEDIA_FORMATS)
        raise BookingSeatsAppError(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            f'Поддерживаются только форматы {formats}',
        )

    async def _persist_media(
        self,
        content: bytes,
        user: User,
    ) -> uuid.UUID:
        """Конвертирует изображение в JPG, сохранит на диск и вернет его ID."""
        media_id = uuid.uuid4()
        file_path = self._get_media_path(media_id)

        def _write_file() -> None:
            jpg_content = self._convert_to_jpg(content)
            ct.MEDIA_DIR.mkdir(parents=True, exist_ok=True)
            file_path.write_bytes(jpg_content)

        try:
            await asyncio.to_thread(_write_file)
        except (OSError, UnidentifiedImageError) as exc:
            self.log_warning(
                f'Пользователь {user.id} не смог загрузить изображение: {exc}',
            )
            raise BookingSeatsAppError(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                'Ошибка сохранения файла',
            ) from exc

        return media_id

    async def _load_media(self, media_id: uuid.UUID) -> bytes:
        """Загрузит JPG-изображение с диска по media_id."""
        file_path = self._get_media_path(media_id)
        if not file_path.is_file():
            raise FileNotFoundError(media_id)

        return await asyncio.to_thread(file_path.read_bytes)

    async def upload(
        self,
        file: UploadFile,
        user: User,
    ) -> MediaInfo:
        """Загрузит изображение на сервер и вернет его ID."""
        content = await self._read_upload_file(file, user)
        media_id = await self._persist_media(content, user)

        self.log_info(
            f'Пользователь {user.id} загрузил изображение {media_id}',
        )
        return MediaInfo(media_id=media_id)

    async def get_image(self, media_id: uuid.UUID) -> bytes:
        """Вернет изображение в бинарном формате JPG."""
        try:
            content = await self._load_media(media_id)
        except FileNotFoundError:
            raise BookingSeatsAppError(
                status.HTTP_404_NOT_FOUND,
                'Данные не найдены',
            )

        self.log_info(f'Получено изображение {media_id}')
        return content


media_service = MediaService()
