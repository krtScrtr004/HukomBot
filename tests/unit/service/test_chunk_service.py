import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
from uuid import UUID, uuid4
from psycopg import AsyncConnection

from backend.hukom_bot.service.chunk_service import ChunkService
from backend.hukom_bot.schema.chunk_schema import ChunkCreate, ChunkSearchVector, ChunkSearchKeyword
from backend.hukom_bot.exception.chunk_exception import ChunkFileException


class TestChunkService:
    """Tests for ChunkService methods."""

    @pytest.fixture
    def mock_chunk_repo(self):
        """Mock ChunkRepository."""
        repo = MagicMock()
        repo.create_many = AsyncMock()
        repo.search_vector = AsyncMock(return_value=[])
        repo.search = AsyncMock(return_value=[])
        repo.count_all = AsyncMock(return_value=100)
        return repo

    @pytest.fixture
    def chunk_service(self, mock_chunk_repo):
        """Create ChunkService instance with mocked dependencies."""
        return ChunkService(chunk_repo=mock_chunk_repo)

    # =========================================================================
    # Repository Delegation Tests
    # =========================================================================

    @pytest.mark.asyncio
    async def test_create_many_delegates_to_repo(self, chunk_service, mock_chunk_repo):
        """create_many() should delegate to chunk_repo.create_many()."""
        chunks = [
            ChunkCreate(document_id=uuid4(), chunk_number=1, chunk_text="Chunk 1"),
            ChunkCreate(document_id=uuid4(), chunk_number=2, chunk_text="Chunk 2"),
        ]
        connection = MagicMock()

        await chunk_service.create_many(chunks, connection=connection)

        mock_chunk_repo.create_many.assert_called_once_with(chunks, connection)

    @pytest.mark.asyncio
    async def test_search_vector_delegates_to_repo(self, chunk_service, mock_chunk_repo):
        """search_vector() should delegate to chunk_repo.search_vector()."""
        search_param = ChunkSearchVector(embeddings=[0.1] * 384, limit=10)
        connection = MagicMock()

        await chunk_service.search_vector(search_param, connection=connection)

        mock_chunk_repo.search_vector.assert_called_once_with(search_param, connection)

    @pytest.mark.asyncio
    async def test_search_keyword_delegates_to_repo(self, chunk_service, mock_chunk_repo):
        """search_keyword() should delegate to chunk_repo.search()."""
        search_param = ChunkSearchKeyword(text="test", limit=10)
        connection = MagicMock()

        await chunk_service.search_keyword(search_param, connection=connection)

        mock_chunk_repo.search.assert_called_once_with(search_param, connection)

    @pytest.mark.asyncio
    async def test_count_all_delegates_to_repo(self, chunk_service, mock_chunk_repo):
        """count_all() should delegate to chunk_repo.count_all()."""
        connection = MagicMock()

        await chunk_service.count_all(connection=connection)

        mock_chunk_repo.count_all.assert_called_once_with(date_range=None, connection=connection)

    # =========================================================================
    # extract_text_to_chunks Tests
    # =========================================================================

    @pytest.mark.asyncio
    async def test_extract_text_to_chunks_success(self, chunk_service):
        """extract_text_to_chunks() should return chunks on success."""
        file_path = Path("test.pdf")
        expected_chunks = [
            {"document": "Chunk 1 text", "section": "Section 1"},
            {"document": "Chunk 2 text", "section": "Section 2"},
        ]

        with patch("backend.hukom_bot.service.chunk_service.run_in_threadpool") as mock_run:
            mock_run.return_value = expected_chunks

            result = await chunk_service.extract_text_to_chunks(file_path)

            assert result == expected_chunks
            mock_run.assert_called_once()

    @pytest.mark.asyncio
    async def test_extract_text_to_chunks_empty_raises_exception(self, chunk_service):
        """extract_text_to_chunks() should raise ChunkFileException when no chunks extracted."""
        file_path = Path("empty.pdf")

        with patch("backend.hukom_bot.service.chunk_service.run_in_threadpool") as mock_run:
            mock_run.return_value = []

            with pytest.raises(ChunkFileException) as exc_info:
                await chunk_service.extract_text_to_chunks(file_path)

            assert "No chunks extracted from file" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_extract_text_to_chunks_none_raises_exception(self, chunk_service):
        """extract_text_to_chunks() should raise ChunkFileException when None returned."""
        file_path = Path("corrupt.pdf")

        with patch("backend.hukom_bot.service.chunk_service.run_in_threadpool") as mock_run:
            mock_run.return_value = None

            with pytest.raises(ChunkFileException) as exc_info:
                await chunk_service.extract_text_to_chunks(file_path)

            assert "No chunks extracted from file" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_extract_text_to_chunks_uses_semaphore(self, chunk_service):
        """extract_text_to_chunks() should use semaphore for OCR concurrency control."""
        file_path = Path("test.pdf")
        expected_chunks = [{"document": "Chunk 1", "section": "Sec 1"}]

        with patch("backend.hukom_bot.service.chunk_service.run_in_threadpool") as mock_run, \
            patch("backend.hukom_bot.service.chunk_service.ocr_semaphor") as mock_semaphore:
            mock_run.return_value = expected_chunks
            mock_semaphore.__aenter__ = AsyncMock()
            mock_semaphore.__aexit__ = AsyncMock()

            result = await chunk_service.extract_text_to_chunks(file_path)

            assert result == expected_chunks
            mock_semaphore.__aenter__.assert_called_once()
            mock_semaphore.__aexit__.assert_called_once()