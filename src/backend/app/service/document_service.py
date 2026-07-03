import magic
import tempfile
import asyncio

from uuid import UUID
from pathlib import Path
from fastapi.concurrency import run_in_threadpool

from backend.app.enum.upload_status import UploadStatus
from backend.app.database.database import Database
from backend.app.schema.chunk_schema import ChunkCreate
from backend.app.repository.chunk_repository import ChunkRepository
from backend.app.schema.document_schema import DocumentCreate, DocumentUpdate
from backend.app.repository.document_repository import DocumentRepository

from backend.app.exception.chunk_exception import ChunkFileException
from backend.app.exception.document_exception import InvalidDocumentTypeException

from backend.app.util.extract_text_from_pdf import extract_text_from_pdf

ocr_semaphor = asyncio.Semaphore(
    1
)  # Allow only 1 OCR process to use GPU at the same time


class DocumentService:
    ALLOWED_FILE_TYPES = {"application/pdf"}

    def __init__(self, db: Database):
        self.db = db

        self.document_repo = DocumentRepository(db=db)
        self.chunk_repo = ChunkRepository(db=db)

    async def create_pending_document(self, file_name: str, contents: bytes):
        suffix = Path(file_name).suffix.lower()

        mime = magic.from_buffer(contents, mime=True)
        if mime not in DocumentService.ALLOWED_FILE_TYPES:
            raise InvalidDocumentTypeException("File type not allowed")

        created_document = await self.document_repo.create(
            DocumentCreate(
                title=file_name,
                file_type=suffix,
            )
        )  # Create document instance

        return created_document

    async def process_document_pdf_upload(
        self, document_id: UUID, filename: str, contents: bytes
    ):
        try:
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

            await self.chunk_repo.create_many(list(document_chunks.values()))

            # Set document upload status to COMPLETED
            await self.document_repo.update(
                DocumentUpdate(id=document_id, update_status=UploadStatus.COMPLETED)
            )
        except Exception as ex:
            # Set document upload status to FAILD
            await self.document_repo.update(
                DocumentUpdate(
                    id=document_id,
                    update_status=UploadStatus.FAILED,
                    update_error=str(ex),
                )
            )
