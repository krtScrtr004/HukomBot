import pytest
from unittest.mock import patch, MagicMock

from backend.hukom_bot.util.file_utilities import get_mime_type, is_valid_file_type


class TestFileUtilities:
    """Tests for file_utilities module."""

    # =========================================================================
    # get_mime_type Tests
    # =========================================================================

    def test_get_mime_type_pdf(self):
        """get_mime_type() should return correct MIME type for PDF."""
        pdf_content = b"%PDF-1.4\n%content"
        
        with patch("magic.from_buffer") as mock_from_buffer:
            mock_from_buffer.return_value = "application/pdf"
            result = get_mime_type(pdf_content)
            
            assert result == "application/pdf"
            mock_from_buffer.assert_called_once_with(pdf_content, mime=True)

    def test_get_mime_type_text(self):
        """get_mime_type() should return correct MIME type for text."""
        text_content = b"This is plain text"
        
        with patch("magic.from_buffer") as mock_from_buffer:
            mock_from_buffer.return_value = "text/plain"
            result = get_mime_type(text_content)
            
            assert result == "text/plain"

    def test_get_mime_type_image(self):
        """get_mime_type() should return correct MIME type for images."""
        image_content = b"\x89PNG\r\n\x1a\n"
        
        with patch("magic.from_buffer") as mock_from_buffer:
            mock_from_buffer.return_value = "image/png"
            result = get_mime_type(image_content)
            
            assert result == "image/png"

    # =========================================================================
    # is_valid_file_type Tests
    # =========================================================================

    def test_is_valid_file_type_valid_pdf(self):
        """is_valid_file_type() should return True for allowed PDF."""
        pdf_content = b"%PDF-1.4"
        allowed_types = {"application/pdf"}

        with patch("backend.hukom_bot.util.file_utilities.get_mime_type") as mock_get_mime:
            mock_get_mime.return_value = "application/pdf"
            result = is_valid_file_type(pdf_content, allowed_types)
            
            assert result is True

    def test_is_valid_file_type_invalid_type(self):
        """is_valid_file_type() should return False for disallowed type."""
        content = b"some content"
        allowed_types = {"application/pdf"}

        with patch("backend.hukom_bot.util.file_utilities.get_mime_type") as mock_get_mime:
            mock_get_mime.return_value = "text/plain"
            result = is_valid_file_type(content, allowed_types)
            
            assert result is False

    def test_is_valid_file_type_with_set(self):
        """is_valid_file_type() should work with set of allowed types."""
        content = b"content"
        allowed_types = {"application/pdf", "image/png", "image/jpeg"}

        with patch("backend.hukom_bot.util.file_utilities.get_mime_type") as mock_get_mime:
            mock_get_mime.return_value = "image/jpeg"
            result = is_valid_file_type(content, allowed_types)
            
            assert result is True

    def test_is_valid_file_type_with_list(self):
        """is_valid_file_type() should work with list of allowed types."""
        content = b"content"
        allowed_types = ["application/pdf", "image/png"]

        with patch("backend.hukom_bot.util.file_utilities.get_mime_type") as mock_get_mime:
            mock_get_mime.return_value = "application/pdf"
            result = is_valid_file_type(content, allowed_types)
            
            assert result is True

    def test_is_valid_file_type_empty_allowed_types(self):
        """is_valid_file_type() should return False for empty allowed types."""
        content = b"content"
        allowed_types = set()

        with patch("backend.hukom_bot.util.file_utilities.get_mime_type") as mock_get_mime:
            mock_get_mime.return_value = "application/pdf"
            result = is_valid_file_type(content, allowed_types)
            
            assert result is False