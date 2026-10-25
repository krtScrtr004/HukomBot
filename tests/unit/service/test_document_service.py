import pytest
import pytest_asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4
from pathlib import Path

from backend.hukom_bot.service.document_service import DocumentService
from backend.hukom_bot.schema.document_schema import DocumentCreate, DocumentUpdate, DocumentSearch, DocumentGetAll, DocumentMetadata
from backend.hukom_bot.enum.legal_document_type import LegalDocumentType
from backend.hukom_bot.exception.app_exception import NotFoundException


class TestDocumentService:
    """Tests for DocumentService methods."""

    @pytest.fixture
    def mock_document_repo(self):
        """Mock DocumentRepository."""
        repo = MagicMock()
        repo.create = AsyncMock(return_value={"id": uuid4()})
        repo.update = AsyncMock()
        repo.get_by_id = AsyncMock(return_value=None)
        repo.get_by_digest = AsyncMock(return_value=None)
        repo.search = AsyncMock(return_value=[])
        repo.all = AsyncMock(return_value=[])
        repo.count_all = AsyncMock(return_value=100)
        repo.count_by_upload_status = AsyncMock(return_value={})
        repo.count_weekly = AsyncMock(return_value=[])
        repo.count_monthly_upload = AsyncMock(return_value={})
        repo.count_registration = AsyncMock(return_value=5)
        repo.count_by_document_type = AsyncMock(return_value={})
        repo.delete = AsyncMock()
        repo.delete_many = AsyncMock()
        repo.get_upload_status_by_id = AsyncMock(return_value=None)
        return repo

    @pytest.fixture
    def mock_embedding_service(self):
        """Mock EmbeddingService."""
        return MagicMock()

    @pytest.fixture
    def mock_file_storage_service(self):
        """Mock FileStorageService."""
        service = MagicMock()
        service.get_pending_file = MagicMock(return_value=Path("test.pdf"))
        return service

    @pytest.fixture
    def document_service(self, mock_document_repo, mock_embedding_service, mock_file_storage_service):
        """Create DocumentService instance with mocked dependencies."""
        return DocumentService(
            document_repo=mock_document_repo,
            embedding_service=mock_embedding_service,
            file_storage_service=mock_file_storage_service,
        )

    # =========================================================================
    # Repository Delegation Tests
    # =========================================================================

    @pytest.mark.asyncio
    async def test_create_delegates_to_repo(self, document_service, mock_document_repo):
        """create() should delegate to document_repo.create()."""
        doc_data = DocumentCreate(
            original_file_name="test.pdf",
            upload_file_name=uuid4(),
            document_type=LegalDocumentType.CONTRACT,
            file_type=".pdf",
            digest=b"a" * 32,
            uploader_id=uuid4(),
        )
        connection = MagicMock()

        result = await document_service.create(doc_data, connection=connection)

        mock_document_repo.create.assert_called_once_with(doc_data, connection)

    @pytest.mark.asyncio
    async def test_update_delegates_to_repo(self, document_service, mock_document_repo):
        """update() should delegate to document_repo.update()."""
        update_data = DocumentUpdate(
            id=uuid4(),
            upload_status="completed",
        )
        connection = MagicMock()

        await document_service.update(update_data, connection=connection)

        mock_document_repo.update.assert_called_once_with(update_data, connection)

    @pytest.mark.asyncio
    async def test_get_by_id_delegates_to_repo(self, document_service, mock_document_repo):
        """get_by_id() should delegate to document_repo.get_by_id()."""
        doc_id = uuid4()
        connection = MagicMock()

        await document_service.get_by_id(doc_id, connection=connection)

        mock_document_repo.get_by_id.assert_called_once_with(doc_id, connection)

    @pytest.mark.asyncio
    async def test_get_by_digest_delegates_to_repo(self, document_service, mock_document_repo):
        """get_by_digest() should delegate to document_repo.get_by_digest()."""
        digest = b"a" * 32
        connection = MagicMock()

        await document_service.get_by_digest(digest, connection=connection)

        mock_document_repo.get_by_digest.assert_called_once_with(digest, connection)

    @pytest.mark.asyncio
    async def test_search_delegates_to_repo(self, document_service, mock_document_repo):
        """search() should delegate to document_repo.search()."""
        param = DocumentSearch(query="test", limit=10)
        connection = MagicMock()

        await document_service.search(param, connection=connection)

        mock_document_repo.search.assert_called_once_with(param=param, connection=connection)

    @pytest.mark.asyncio
    async def test_all_delegates_to_repo(self, document_service, mock_document_repo):
        """all() should delegate to document_repo.all()."""
        param = DocumentGetAll(limit=10)
        connection = MagicMock()

        await document_service.all(param, connection=connection)

        mock_document_repo.all.assert_called_once_with(param=param, connection=connection)

    @pytest.mark.asyncio
    async def test_count_all_delegates_to_repo(self, document_service, mock_document_repo):
        """count_all() should delegate to document_repo.count_all()."""
        connection = MagicMock()

        await document_service.count_all(connection=connection)

        mock_document_repo.count_all.assert_called_once_with(date_range=None, connection=connection)

    @pytest.mark.asyncio
    async def test_count_by_upload_status_delegates_to_repo(self, document_service, mock_document_repo):
        """count_by_upload_status() should delegate to document_repo.count_by_upload_status()."""
        connection = MagicMock()

        await document_service.count_by_upload_status(connection=connection)

        mock_document_repo.count_by_upload_status.assert_called_once_with(date_range=None, connection=connection)

    @pytest.mark.asyncio
    async def test_count_weekly_delegates_to_repo(self, document_service, mock_document_repo):
        """count_weekly() should delegate to document_repo.count_weekly()."""
        connection = MagicMock()

        await document_service.count_weekly(connection=connection)

        mock_document_repo.count_weekly.assert_called_once_with(connection=connection)

    @pytest.mark.asyncio
    async def test_count_monthly_upload_delegates_to_repo(self, document_service, mock_document_repo):
        """count_monthly_upload() should delegate to document_repo.count_monthly_upload()."""
        connection = MagicMock()

        await document_service.count_monthly_upload(connection=connection)

        mock_document_repo.count_monthly_upload.assert_called_once_with(year=datetime.now().year, connection=connection)

    @pytest.mark.asyncio
    async def test_count_registration_delegates_to_repo(self, document_service, mock_document_repo):
        """count_registration() should delegate to document_repo.count_registration()."""
        connection = MagicMock()

        await document_service.count_registration(connection=connection)

        mock_document_repo.count_registration.assert_called_once_with(interval_days=360, connection=connection)

    @pytest.mark.asyncio
    async def test_count_by_document_type_delegates_to_repo(self, document_service, mock_document_repo):
        """count_by_document_type() should delegate to document_repo.count_by_document_type()."""
        connection = MagicMock()

        await document_service.count_by_document_type(connection=connection)

        mock_document_repo.count_by_document_type.assert_called_once_with(date_range=None, connection=connection)

    @pytest.mark.asyncio
    async def test_delete_delegates_to_repo(self, document_service, mock_document_repo):
        """delete() should delegate to document_repo.delete()."""
        doc_id = uuid4()
        connection = MagicMock()

        await document_service.delete(doc_id, connection=connection)

        mock_document_repo.delete.assert_called_once_with(id=doc_id, connection=connection)

    @pytest.mark.asyncio
    async def test_delete_many_delegates_to_repo(self, document_service, mock_document_repo):
        """delete_many() should delegate to document_repo.delete_many()."""
        ids = [uuid4(), uuid4()]
        connection = MagicMock()

        await document_service.delete_many(ids, connection=connection)

        mock_document_repo.delete_many.assert_called_once_with(ids=ids, connection=connection)

    # =========================================================================
    # get_upload_status Tests
    # =========================================================================

    @pytest.mark.asyncio
    async def test_get_upload_status_found(self, document_service, mock_document_repo):
        """get_upload_status() should return status when document exists."""
        doc_id = uuid4()
        mock_document_repo.get_upload_status_by_id.return_value = "completed"

        result = await document_service.get_upload_status(doc_id)

        assert result == "completed"
        mock_document_repo.get_upload_status_by_id.assert_called_once_with(doc_id)

    @pytest.mark.asyncio
    async def test_get_upload_status_not_found_raises_404(self, document_service, mock_document_repo):
        """get_upload_status() should raise NotFoundException when document not found."""
        doc_id = uuid4()
        mock_document_repo.get_upload_status_by_id.return_value = None

        with pytest.raises(NotFoundException) as exc_info:
            await document_service.get_upload_status(doc_id)

        assert exc_info.value.code == "DOCUMENT_NOT_FOUND"
        assert "Document not found" in exc_info.value.message

    # =========================================================================
    # File Validation Tests
    # =========================================================================

    def test_is_valid_file_type_pdf(self, document_service):
        """is_valid_file_type() should return True for PDF files."""
        pdf_content = b"%PDF-1.4\n%content"
        result = document_service.is_valid_file_type(pdf_content)
        assert result is True

    def test_is_valid_file_type_invalid(self, document_service):
        """is_valid_file_type() should return False for non-PDF files."""
        text_content = b"This is a text file"
        result = document_service.is_valid_file_type(text_content)
        assert result is False

    # =========================================================================
    # build_metadata Tests
    # =========================================================================

    def test_build_metadata_creates_correct_metadata(self, document_service):
        """build_metadata() should create correct DocumentMetadata."""
        file_path = Path("test_document.pdf")
        contents = b"%PDF-1.4 content"
        document_type = LegalDocumentType.CONTRACT

        metadata = document_service.build_metadata(
            file_path=file_path,
            contents=contents,
            document_type=document_type,
        )

        assert isinstance(metadata, DocumentMetadata)
        assert metadata.file_path == file_path
        assert metadata.original_file_name == "test_document"
        assert isinstance(metadata.upload_file_name, UUID)
        assert metadata.document_type == document_type
        assert metadata.suffix == ".pdf"
        assert isinstance(metadata.digest, bytes)
        assert len(metadata.digest) == 32  # SHA256 digest length

    def test_build_metadata_with_custom_digest(self, document_service):
        """build_metadata() should use provided digest when given."""
        file_path = Path("test.pdf")
        contents = b"content"
        document_type = LegalDocumentType.CONTRACT
        custom_digest = b"custom" + b"0" * 26  # 32 bytes

        metadata = document_service.build_metadata(
            file_path=file_path,
            contents=contents,
            document_type=document_type,
            digest=custom_digest,
        )

        assert metadata.digest == custom_digest

    def test_build_metadata_lowercase_suffix(self, document_service):
        """build_metadata() should use lowercase suffix."""
        file_path = Path("TEST.PDF")
        contents = b"%PDF-1.4"
        document_type = LegalDocumentType.CONTRACT

        metadata = document_service.build_metadata(
            file_path=file_path,
            contents=contents,
            document_type=document_type,
        )

        assert metadata.suffix == ".pdf"

    def test_build_metadata_original_file_name_stem(self, document_service):
        """build_metadata() should use file stem as original_file_name."""
        file_path = Path("/path/to/my_document.pdf")
        contents = b"%PDF-1.4"
        document_type = LegalDocumentType.CONTRACT

        metadata = document_service.build_metadata(
            file_path=file_path,
            contents=contents,
            document_type=document_type,
        )

        assert metadata.original_file_name == "my_document"