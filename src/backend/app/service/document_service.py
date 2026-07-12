import magic
import asyncio
import logging
import hashlib

from uuid import UUID, uuid4
from pathlib import Path
from fastapi import UploadFile, BackgroundTasks, HTTPException
from fastapi.concurrency import run_in_threadpool

from backend.app.enum.upload_status import UploadStatus
from backend.app.enum.legal_document_type import LegalDocumentType
from backend.app.database.database import Database
from backend.app.schema.chunk_schema import ChunkCreate
from backend.app.repository.chunk_repository import ChunkRepository
from backend.app.model.document_model import Document
from backend.app.schema.document_schema import (
    DocumentCreate,
    DocumentUpdate,
    DocumentUploadResponse,
    DocumentUploadStatusResponse,
    ApproveDocumentUpload,
)
from backend.app.repository.document_repository import DocumentRepository
from backend.app.service.embedding_service import EmbedService
from backend.app.service.file_storage_service import FileStorageService

from backend.app.exception.chunk_exception import ChunkFileException
from backend.app.exception.document_exception import InvalidDocumentTypeException

from backend.app.util.extract_text_from_pdf import extract_text_from_pdf

logger = logging.getLogger(__name__)

ocr_semaphor = asyncio.Semaphore(
    1
)  # Allow only 1 OCR process to use GPU at the same time


class DocumentService:
    ALLOWED_FILE_TYPES = {"application/pdf"}

    def __init__(self, db: Database):
        self.__document_repo = DocumentRepository(db=db)
        self.__chunk_repo = ChunkRepository(db=db)

        self.__embed_service = EmbedService()
        self.__file_storage_service = FileStorageService()

    async def create_pending_document(
        self, file: UploadFile, document_type: LegalDocumentType
    ):
        contents = await file.read()

        # Check if valid file type
        mime = magic.from_buffer(contents, mime=True)
        if mime not in DocumentService.ALLOWED_FILE_TYPES:
            raise InvalidDocumentTypeException("File type not allowed")

        file_path = Path(file.filename)
        original_file_name = file_path.stem
        upload_file_name = uuid4()
        suffix = file_path.suffix.lower()
        digest = hashlib.sha256(contents).digest()

        try:
            # Check for existing document by file digest
            existing_document = await self.__document_repo.get_by_digest(digest)
            if existing_document:
                logger.info("Document with id: %s already exists", existing_document.id)
                return DocumentUploadResponse(
                    messages=["File already exisits"],
                    document_id=existing_document.id,
                    status=existing_document.upload_status,
                )

            # Save pending document to data/pending/ folder
            await self.__file_storage_service.save_to_pending(
                upload_file_name, contents, suffix
            )

            created_document = await self.__document_repo.create(
                DocumentCreate(
                    original_file_name=original_file_name,
                    upload_file_name=upload_file_name,
                    document_type=document_type,
                    file_type=suffix,
                    digest=digest,
                )
            )  # Create document instance

            logger.info(
                "Document with id: %s inserted in the db and is pending for embedding process",
                created_document.id,
            )
            return DocumentUploadResponse(
                messages=["File upload is pending for approval"],
                document_id=created_document.id,
                status=UploadStatus.PENDING,
            )
        except Exception:
            # Rollback file creation
            self.__file_storage_service.delete_from_pending(
                f"{upload_file_name}.{suffix.lstrip(".")}"
            )
            raise

    async def approve_document_upload(
        self,
        document_id: UUID,
        payload: ApproveDocumentUpload,
        background_tasks: BackgroundTasks,
    ):
        document = await self.__document_repo.get_by_id(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        if document.upload_status == UploadStatus.COMPLETED:
            return DocumentUploadResponse(
                messages=["File upload completed"],
                document_id=document_id,
                status=UploadStatus.COMPLETED,
            )

        file = self.__file_storage_service.get_pending_file(
            document.upload_file_name, document.file_type
        )

        # Update document_type if not None in request body
        document.document_type = (
            payload.document_type
            if payload.document_type is not None
            else document.document_type
        )
        background_tasks.add_task(self.__process_document_pdf_upload, document, file)

        return DocumentUploadResponse(
            messages=["File upload is ongoing"],
            document_id=document_id,
            status=UploadStatus.ONGOING,
        )

    async def __process_document_pdf_upload(self, document: Document, file: Path):
        try:
            # Set document upload status to ONGOING
            await self.__document_repo.update(
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

            chunks = None
            async with ocr_semaphor:
                chunks = await run_in_threadpool(extract_text_from_pdf, file)
            if not chunks:
                raise ChunkFileException("No chunks extracted from file")

            # Create the chunk models
            document_chunks = {}
            for i, chunk in enumerate(chunks):
                document_chunks[i] = ChunkCreate(
                    document_id=document.id,
                    chunk_number=i,
                    chunk_text=chunk["document"],
                    section=chunk["section"],
                )

            texts = [chunk["document"] for chunk in chunks]
            embeddings = self.__embed_service.embed_documents(texts)

            # Map embeddings back to the chunk models
            for i, embedding in enumerate(embeddings):
                chunk_model = document_chunks.get(i)
                if chunk_model:
                    chunk_model.embedding = embedding

            await self.__chunk_repo.create_many(list(document_chunks.values()))

            # Set document upload status to COMPLETED
            await self.__document_repo.update(
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
            await self.__file_storage_service.delete_from_pending(file.name)

            logger.info("Document %s successfully deleted", file.name)
        except Exception as ex:
            # Set document upload status to FAILED
            await self.__document_repo.update(
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

    async def get_upload_status(self, document_id: UUID):
        upload_status = await self.__document_repo.get_upload_status_by_id(document_id)
        if not upload_status:
            raise HTTPException(status_code=404, detail="Document not found")

        return DocumentUploadStatusResponse(
            messages=[f"Document upload status is: {upload_status.display_name()}"],
            status_value=upload_status,
        )
