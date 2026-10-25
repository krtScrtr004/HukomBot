import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4
from pathlib import Path

from backend.hukom_bot.service.file_storage_service import FileStorageService


class TestFileStorageService:
    """Tests for FileStorageService methods."""

    @pytest.fixture
    def temp_data_path(self, tmp_path):
        """Create a temporary data directory."""
        data_path = tmp_path / "data"
        data_path.mkdir(parents=True, exist_ok=True)
        return data_path

    @pytest.fixture
    def file_storage_service(self, temp_data_path):
        """Create FileStorageService instance with temporary data path."""
        with patch("backend.hukom_bot.service.file_storage_service.get_project_root") as mock_root:
            mock_root.return_value = temp_data_path
            service = FileStorageService()
            return service

    # =========================================================================
    # read_file Tests
    # =========================================================================

    @pytest.mark.asyncio
    async def test_read_file_returns_bytes(self, file_storage_service):
        """read_file() should return file contents as bytes."""
        test_file = file_storage_service._FileStorageService__pending_path() / "test.txt"
        test_file.write_bytes(b"file content")
        
        with patch("backend.hukom_bot.service.file_storage_service.run_in_threadpool") as mock_run:
            mock_run.return_value = b"file content"
            
            result = await file_storage_service.read_file(test_file)
            
            assert result == b"file content"
            mock_run.assert_called_once_with(test_file.read_bytes)

    # =========================================================================
    # save_to_pending Tests
    # =========================================================================

    @pytest.mark.asyncio
    async def test_save_to_pending_writes_file(self, file_storage_service):
        """save_to_pending() should write file to pending directory."""
        upload_file_name = uuid4()
        contents = b"file content"
        suffix = "pdf"
        
        with patch("backend.hukom_bot.service.file_storage_service.run_in_threadpool") as mock_run:
            mock_run.return_value = None
            
            result = await file_storage_service.save_to_pending(upload_file_name, contents, suffix)
            
            assert isinstance(result, Path)
            assert str(upload_file_name) in str(result)
            assert suffix in str(result)
            mock_run.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_to_pending_creates_pending_directory(self, file_storage_service):
        """save_to_pending() should create pending directory if it doesn't exist."""
        upload_file_name = uuid4()
        contents = b"content"
        suffix = "pdf"
        
        with patch("backend.hukom_bot.service.file_storage_service.run_in_threadpool") as mock_run:
            mock_run.return_value = None
            
            await file_storage_service.save_to_pending(upload_file_name, contents, suffix)
            
            # Check that mkdir was called on pending path
            pending_path = file_storage_service._FileStorageService__pending_path()
            assert pending_path.exists()

    @pytest.mark.asyncio
    async def test_save_to_pending_strips_dot_from_suffix(self, file_storage_service):
        """save_to_pending() should strip leading dot from suffix."""
        upload_file_name = uuid4()
        contents = b"content"
        suffix = ".pdf"  # With leading dot
        
        with patch("backend.hukom_bot.service.file_storage_service.run_in_threadpool") as mock_run:
            mock_run.return_value = None
            
            result = await file_storage_service.save_to_pending(upload_file_name, contents, suffix)
            
            assert str(upload_file_name) in str(result)
            # Should not have double dots
            assert result.suffix == ".pdf"  # Only one dot

    # =========================================================================
    # get_pending_file Tests
    # =========================================================================

    def test_get_pending_file_returns_path(self, file_storage_service):
        """get_pending_file() should return Path to file."""
        upload_file_name = uuid4()
        suffix = "pdf"
        
        # First create the file
        pending_path = file_storage_service._FileStorageService__pending_path()
        test_file = pending_path / f"{upload_file_name}.{suffix}"
        test_file.touch()
        
        path = file_storage_service.get_pending_file(upload_file_name, suffix)
        
        assert isinstance(path, Path)
        assert str(upload_file_name) in str(path)
        assert suffix in str(path)

    def test_get_pending_file_raises_not_found(self, file_storage_service):
        """get_pending_file() should raise FileNotFoundError for non-existent files."""
        upload_file_name = uuid4()
        suffix = "pdf"
        
        with pytest.raises(FileNotFoundError) as exc_info:
            file_storage_service.get_pending_file(upload_file_name, suffix)
        
        assert "No file found" in str(exc_info.value)

    # =========================================================================
    # delete_from_pending Tests
    # =========================================================================

    @pytest.mark.asyncio
    async def test_delete_from_pending_unlinks_file(self, file_storage_service):
        """delete_from_pending() should unlink the file."""
        file_name = "test_file.pdf"
        
        # Create the file first
        pending_path = file_storage_service._FileStorageService__pending_path()
        test_file = pending_path / file_name
        test_file.touch()
        
        await file_storage_service.delete_from_pending(file_name)
        
        assert not test_file.exists()

    @pytest.mark.asyncio
    async def test_delete_from_pending_uses_pending_path(self, file_storage_service):
        """delete_from_pending() should use pending path."""
        file_name = "test.pdf"
        
        # Create the file first
        pending_path = file_storage_service._FileStorageService__pending_path()
        test_file = pending_path / file_name
        test_file.touch()
        
        await file_storage_service.delete_from_pending(file_name)
        
        assert not test_file.exists()