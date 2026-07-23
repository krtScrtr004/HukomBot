import logging
from uuid import UUID
from pathlib import Path
from fastapi import UploadFile

from backend.app.enum.upload_status import UploadStatus
from backend.app.enum.legal_document_type import LegalDocumentType
from backend.app.model.document_model import Document
from backend.app.schema.document_schema import *
from backend.app.schema.chunk_schema import ChunkCreate
from backend.app.schema.orchistrator_schema import OrchistratorResult
from backend.app.service.chunk_service import ChunkService
from backend.app.service.document_service import DocumentService
from backend.app.service.embedding_service import EmbeddingService
from backend.app.service.file_storage_service import FileStorageService
from backend.app.exception.app_exception import NotFoundException
from backend.app.exception.document_exception import InvalidDocumentTypeException
from backend.app.util.document_caster import DocumentCaster

logger = logging.getLogger(__name__)


class DocumentOrchistrator:
    def __init__(
        self,
        chunk_service: ChunkService,
        document_service: DocumentService,
        embedding_service: EmbeddingService,
        file_storage_service: FileStorageService,
    ):
        self._chunk_service = chunk_service
        self._document_service = document_service
        self._embedding_service = embedding_service
        self._file_storage_service = file_storage_service

    async def create_pending(
        self, user_id: UUID, file: UploadFile, document_type: LegalDocumentType
    ) -> OrchistratorResult:
        contents = await file.read()

        # Check if valid file type
        if not self._document_service.is_valid_file_type(contents):
            raise InvalidDocumentTypeException(
                message="File type not allowed",
                details=[
                    f"Only {', '.join(type.removeprefix("application/") for type in DocumentService.ALLOWED_FILE_TYPES)} are allowed"
                ],
            )

        metadata = self._document_service.build_metadata(
            file_path=Path(file.filename),
            contents=contents,
            document_type=document_type,
        )

        try:
            # Check for existing document by file digest
            existing_document = await self._document_service.get_by_digest(
                metadata.digest
            )
            if existing_document:
                logger.info("Document with id: %s already exists", existing_document.id)
                return OrchistratorResult(
                    message="File already exists",
                    data=DocumentCaster.base_to_upload_response(existing_document),
                )

            # Save pending document to data/pending/ folder
            await self._file_storage_service.save_to_pending(
                metadata.upload_file_name, contents, metadata.suffix
            )

            created_document = await self._document_service.create(
                DocumentCreate(
                    original_file_name=metadata.original_file_name,
                    upload_file_name=metadata.upload_file_name,
                    document_type=document_type,
                    file_type=metadata.suffix,
                    digest=metadata.digest,
                    uploader_id=user_id
                )
            )  # Create document instance

            logger.info(
                "Document with id: %s inserted in the db and is pending for embedding process",
                created_document.id,
            )
            return OrchistratorResult(
                message=f"File upload is pending for approval",
                data=DocumentCaster.base_to_upload_response(created_document),
            )
        except Exception as ex:
            logger.exception(str(ex))

            # Rollback file creation
            self._file_storage_service.delete_from_pending(
                f"{metadata.upload_file_name}.{metadata.suffix.lstrip(".")}"
            )
            raise

    async def approve_document_upload(
        self,
        document_id: UUID,
        payload: ApproveDocumentUploadPayload,
    ) -> OrchistratorResult:
        document = await self._document_service.get_by_id(document_id)
        if not document:
            raise NotFoundException(
                code="DOCUMENT_NOT_FOUND", message="Document not found"
            )

        if document.upload_status == UploadStatus.COMPLETED:
            return OrchistratorResult(
                message="File upload completed",
                data={
                    "document": document,
                    "response": DocumentCaster.base_to_upload_response(document),
                },
            )

        # Update document_type if not None in request body
        document.document_type = (
            payload.document_type
            if payload.document_type is not None
            else document.document_type
        )
        document.upload_status = UploadStatus.ONGOING
        await self._document_service.update(
            DocumentUpdate(
                id=document_id,
                document_type=document.document_type,
                upload_status=document.upload_status,
            )
        )

        return OrchistratorResult(
            message="File upload is ongoing",
            data={
                "document": document,
                "response": DocumentUploadResponse(
                    document_id=document_id,
                    status=document.upload_status,
                ),
            },
        )

    async def process_document_pdf_upload(self, document: Document, file: Path):
        try:
            # Set document upload status to ONGOING
            await self._document_service.update(
                DocumentUpdate(
                    id=document.id,
                    document_type=document.document_type,
                    upload_status=UploadStatus.ONGOING,
                    upload_error=None,
                )
            )
            logger.info(
                "Document with id: %s set upload status to ONGOING", document.id
            )

            chunks = await self._chunk_service.extract_text_to_chunks(file)

            # Create the chunk models
            document_chunks = {}
            for i, chunk in enumerate(chunks):
                document_chunks[i] = ChunkCreate(
                    document_id=document.id,
                    chunk_number=i + 1,
                    chunk_text=chunk["document"],
                    section=chunk["section"],
                )

            texts = [chunk["document"] for chunk in chunks]
            embeddings = self._embedding_service.embed_documents(texts)

            # Map embeddings back to the chunk models
            for i, embedding in enumerate(embeddings):
                chunk_model = document_chunks.get(i)
                if chunk_model:
                    chunk_model.embedding = embedding

            await self._chunk_service.create_many(list(document_chunks.values()))

            # Set document upload status to COMPLETED
            await self._document_service.update(
                DocumentUpdate(
                    id=document.id,
                    upload_status=UploadStatus.COMPLETED,
                )
            )

            logger.info(
                "%i chunks created for document with id: %s",
                len(document_chunks),
                document.id,
            )

            logger.info(
                "Document with id: %s set upload status to COMPLETED", document.id
            )

            # Delete file in the server
            await self._file_storage_service.delete_from_pending(file.name)

            logger.info("Document %s successfully deleted", file.name)
        except Exception as ex:
            # Set document upload status to FAILED
            await self._document_service.update(
                DocumentUpdate(
                    id=document.id,
                    upload_status=UploadStatus.FAILED,
                    upload_error=str(ex),
                )
            )

            logger.error(
                "Document with id: %s set upload status to FAILED", document.id
            )

            logger.exception(str(ex))
