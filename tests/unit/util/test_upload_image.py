import pytest
from unittest.mock import patch, MagicMock
from backend.hukom_bot.util.upload_image import upload_to_cloudinary, remove_from_cloudinary
from backend.hukom_bot.schema.util_schema import CloudinaryUploadResponse


class TestUploadImage:
    """Tests for upload_image utility module."""

    # =========================================================================
    # upload_to_cloudinary Tests
    # =========================================================================

    def test_upload_to_cloudinary_returns_response(self):
        """upload_to_cloudinary() should return CloudinaryUploadResponse."""
        file_content = b"fake image data"
        mock_cloudinary_result = {
            "public_id": "test_folder/abc123",
            "secure_url": "https://res.cloudinary.com/test/image/upload/test_folder/abc123",
        }

        with patch("cloudinary.uploader.upload") as mock_upload:
            mock_upload.return_value = mock_cloudinary_result
            
            result = upload_to_cloudinary(file_content)
            
            assert isinstance(result, CloudinaryUploadResponse)
            assert result.public_id == "test_folder/abc123"
            assert str(result.secure_url) == "https://res.cloudinary.com/test/image/upload/test_folder/abc123"
            
            mock_upload.assert_called_once_with(file_content, folder="hukom_bot/images")

    def test_upload_to_cloudinary_with_extra_fields(self):
        """upload_to_cloudinary() should ignore extra fields from Cloudinary."""
        file_content = b"fake image data"
        mock_cloudinary_result = {
            "public_id": "test_folder/abc123",
            "secure_url": "https://res.cloudinary.com/test/image/upload/test_folder/abc123",
            "format": "jpg",
            "width": 100,
            "height": 100,
            "extra_field": "should be ignored",
        }

        with patch("cloudinary.uploader.upload") as mock_upload:
            mock_upload.return_value = mock_cloudinary_result
            
            result = upload_to_cloudinary(file_content)
            
            assert isinstance(result, CloudinaryUploadResponse)
            # extra_field should be ignored due to extra="ignore" in model_validate

    # =========================================================================
    # remove_from_cloudinary Tests
    # =========================================================================

    def test_remove_from_cloudinary_success(self):
        """remove_from_cloudinary() should return True for successful deletion."""
        public_id = "test_folder/abc123"
        mock_result = {"result": "ok"}

        with patch("cloudinary.uploader.destroy") as mock_destroy:
            mock_destroy.return_value = mock_result
            
            result = remove_from_cloudinary(public_id)
            
            assert result is True
            mock_destroy.assert_called_once_with(public_id=public_id)

    def test_remove_from_cloudinary_failure(self):
        """remove_from_cloudinary() should return False for failed deletion."""
        public_id = "test_folder/abc123"
        mock_result = {"result": "not found"}

        with patch("cloudinary.uploader.destroy") as mock_destroy:
            mock_destroy.return_value = mock_result
            
            result = remove_from_cloudinary(public_id)
            
            assert result is False

    def test_remove_from_cloudinary_missing_result(self):
        """remove_from_cloudinary() should return False when result key missing."""
        public_id = "test_folder/abc123"
        mock_result = {}

        with patch("cloudinary.uploader.destroy") as mock_destroy:
            mock_destroy.return_value = mock_result
            
            result = remove_from_cloudinary(public_id)
            
            assert result is False

    def test_remove_from_cloudinary_error_result(self):
        """remove_from_cloudinary() should return False for error result."""
        public_id = "test_folder/abc123"
        mock_result = {"result": "error", "error": "Some error"}

        with patch("cloudinary.uploader.destroy") as mock_destroy:
            mock_destroy.return_value = mock_result
            
            result = remove_from_cloudinary(public_id)
            
            assert result is False