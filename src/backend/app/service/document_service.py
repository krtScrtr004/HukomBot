import magic
import tempfile
import asyncio
import logging

from uuid import UUID, uuid4
from pathlib import Path
from fastapi.concurrency import run_in_threadpool

from backend.app.enum.upload_status import UploadStatus
from backend.app.enum.legal_document_type import LegalDocumentType
from backend.app.database.database import Database
from backend.app.schema.chunk_schema import ChunkCreate
from backend.app.repository.chunk_repository import ChunkRepository
from backend.app.schema.document_schema import DocumentCreate, DocumentUpdate
from backend.app.repository.document_repository import DocumentRepository
from backend.app.service.embed_service import EmbedService

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
        self.db = db

        self.document_repo = DocumentRepository(db=db)
        self.chunk_repo = ChunkRepository(db=db)

        self.embed_service = EmbedService()

    async def create_pending_document(self, file_name: str, document_type: LegalDocumentType, contents: bytes):

        file_path = Path(file_name)
        original_file_name = file_path.stem
        upload_file_name = uuid4()
        suffix = file_path.suffix.lower()

        existing_document = await self.document_repo.get_by_original_file_name(original_file_name)
        if existing_document:
            logging.info("Document with id: %s already exists", existing_document.id)
            return existing_document
        
        mime = magic.from_buffer(contents, mime=True)
        if mime not in DocumentService.ALLOWED_FILE_TYPES:
            raise InvalidDocumentTypeException("File type not allowed")

        created_document = await self.document_repo.create(
            DocumentCreate(
                original_file_name=original_file_name,
                upload_file_name=upload_file_name,
                document_type=document_type,
                file_type=suffix,
            )
        )  # Create document instance

        logging.info(
            "Document with id: %s inserted in the db and is ongoing for embedding process",
            created_document.id,
        )
        return created_document

    async def process_document_pdf_upload(
        self, document_id: UUID, filename: str, contents: bytes
    ):
        try:            
            existing_document = await self.document_repo.get_by_id(document_id)
            if (
                existing_document
                and existing_document.upload_status == UploadStatus.COMPLETED
            ):
                # Do not perform embedding if document is already uploaded
                logging.info("Document's content with id: %s already embeded", document_id)
                return

            # Set document upload status to ONGOING
            await self.document_repo.update(
                DocumentUpdate(
                    id=document_id,
                    upload_status=UploadStatus.ONGOING,
                    upload_error=None,
                )
            )
            
            logging.info(
                "Document with id: %s set upload status to ONGOING", document_id
            )

            suffix = Path(filename).suffix.lower()
            # Create temporary file on disk
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                tmp.write(contents)
                tmp_path = Path(tmp.name)

            chunks = None
            try:
                async with ocr_semaphor:
                    chunks = await run_in_threadpool(extract_text_from_pdf, tmp_path)
                if not chunks:
                    raise ChunkFileException("No chunks extracted from file")
            finally:
                # Clean up temp file regardless of outcome
                tmp_path.unlink(missing_ok=True)

            # Create the chunk models
            document_chunks = {}
            for i, chunk in enumerate(chunks):
                document_chunks[i] = ChunkCreate(
                    document_id=document_id,
                    chunk_number=i,
                    chunk_text=chunk["document"],
                    section=chunk["section"],
                )

            texts = [chunk["document"] for chunk in chunks]
            embeddings = self.embed_service.embed_documents(texts)

            # Map embeddings back to the chunk models
            for i, embedding in enumerate(embeddings):
                chunk_model = document_chunks.get(i)
                if chunk_model:
                    chunk_model.embedding = embedding

            await self.chunk_repo.create_many(list(document_chunks.values()))

            # Set document upload status to COMPLETED
            await self.document_repo.update(
                DocumentUpdate(
                    id=document_id,
                    upload_status=UploadStatus.COMPLETED,
                )
            )

            logging.info(
                "%i chunks created for document with id: %s",
                len(document_chunks),
                document_id,
            )

            logging.info(
                "Document with id: %s set upload status to COMPLETED", document_id
            )
        except Exception as ex:
            # Set document upload status to FAILED
            await self.document_repo.update(
                DocumentUpdate(
                    id=document_id,
                    upload_status=UploadStatus.FAILED,
                    upload_error=str(ex),
                )
            )

            logging.error(
                "Document with id: %s set upload status to FAILED", document_id
            )

            logging.exception(str(ex))
