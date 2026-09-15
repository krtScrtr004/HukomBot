import magic
import hashlib
import logging
from pathlib import Path
from uuid import UUID, uuid4
from psycopg import AsyncConnection
from backend.hukom_bot.schema.mixin import DateRangeableMixin
from backend.hukom_bot.enum.legal_document_type import LegalDocumentType
from backend.hukom_bot.schema.document_schema import *
from backend.hukom_bot.repository.document_repository import DocumentRepository
from backend.hukom_bot.service.embedding_service import EmbeddingService
from backend.hukom_bot.service.file_storage_service import FileStorageService
from backend.hukom_bot.exception.app_exception import NotFoundException
from backend.hukom_bot.util.file_utilities import is_valid_file_type

logger = logging.getLogger(__name__)


class DocumentService:
    ALLOWED_FILE_TYPES = {"application/pdf"}

    def __init__(
        self,
        document_repo: DocumentRepository,
        embedding_service: EmbeddingService,
        file_storage_service: FileStorageService,
    ):
        self._document_repo = document_repo
        self._embedding_service = embedding_service
        self._file_storage_service = file_storage_service

    # Repo ========

    async def create(
        self, document: DocumentCreate, connection: AsyncConnection = None
    ):
        return await self._document_repo.create(document, connection)

    async def update(
        self, document: DocumentUpdate, connection: AsyncConnection = None
    ):
        return await self._document_repo.update(document, connection)

    async def get_by_id(self, id: UUID, connection: AsyncConnection = None):
        return await self._document_repo.get_by_id(id, connection)

    async def get_by_digest(self, digest: bytes, connection: AsyncConnection = None):
        return await self._document_repo.get_by_digest(digest, connection)

    async def search(self, param: DocumentSearch, connection: AsyncConnection = None):
        return await self._document_repo.search(param=param, connection=connection)

    async def all(self, param: DocumentGetAll, connection: AsyncConnection = None):
        return await self._document_repo.all(param=param, connection=connection)

    async def count_all(
        self, date_range: DateRangeableMixin = None, connection: AsyncConnection = None
    ):
        return await self._document_repo.count_all(
            date_range=date_range, connection=connection
        )

    async def count_by_upload_status(
        self, date_range: DateRangeableMixin = None, connection: AsyncConnection = None
    ):
        return await self._document_repo.count_by_upload_status(
            date_range=date_range, connection=connection
        )

    async def count_weekly(self, connection: AsyncConnection = None):
        return await self._document_repo.count_weekly(connection=connection)

    # Others =======

    def get_file_from_storage(self, upload_file_name, file_type):
        return self._file_storage_service.get_pending_file(upload_file_name, file_type)

    async def get_upload_status(self, document_id: UUID):
        upload_status = await self._document_repo.get_upload_status_by_id(document_id)
        if not upload_status:
            raise NotFoundException(
                code="DOCUMENT_NOT_FOUND", message="Document not found"
            )

        return upload_status

    def is_valid_file_type(self, contents: bytes) -> bool:
        return is_valid_file_type(
            content=contents, allowed_file_types=DocumentService.ALLOWED_FILE_TYPES
        )

    def build_metadata(
        self,
        file_path: Path,
        contents: bytes,
        document_type: LegalDocumentType,
        digest: bytes = None,
    ) -> DocumentMetadata:
        return DocumentMetadata(
            file_path=file_path,
            original_file_name=file_path.stem,
            upload_file_name=uuid4(),
            document_type=document_type,
            suffix=file_path.suffix.lower(),
            digest=digest or hashlib.sha256(contents).digest(),
        )
