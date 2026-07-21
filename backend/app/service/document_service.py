import magic
import hashlib
import logging

from pathlib import Path
from uuid import UUID, uuid4
from psycopg import AsyncConnection

from backend.app.enum.legal_document_type import LegalDocumentType

from backend.app.model.document_model import Document
from backend.app.schema.document_schema import *

from backend.app.repository.document_repository import DocumentRepository

from backend.app.service.embedding_service import EmbeddingService
from backend.app.service.file_storage_service import FileStorageService

from backend.app.exception.not_found_exception import NotFoundException


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
        mime = magic.from_buffer(contents, mime=True)
        return mime in DocumentService.ALLOWED_FILE_TYPES

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
