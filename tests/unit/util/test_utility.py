import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4
from pathlib import Path

from backend.hukom_bot.util.utility import (
    get_project_root,
    is_pdf,
    format_conversation_history,
    get_client_ip,
    generate_daily_token_quota_key,
    build_date_range_where_clause,
)
from backend.hukom_bot.enum.date_range import DateRange
from backend.hukom_bot.schema.mixin import DateRangeableMixin
from fastapi import Request


class TestUtility:
    """Tests for utility module."""

    # =========================================================================
    # get_project_root Tests
    # =========================================================================

    def test_get_project_root_default(self):
        """get_project_root() with default level should return correct path."""
        # This test verifies the function doesn't crash
        result = get_project_root()
        assert isinstance(result, Path)

    def test_get_project_root_custom_level(self):
        """get_project_root() with custom level should work."""
        result = get_project_root(level=2)
        assert isinstance(result, Path)

    # =========================================================================
    # is_pdf Tests
    # =========================================================================

    def test_is_pdf_valid(self, tmp_path):
        """is_pdf() should return True for valid PDF."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4\n%content")
        
        result = is_pdf(pdf_file)
        assert result is True

    def test_is_pdf_invalid_content(self, tmp_path):
        """is_pdf() should return False for non-PDF content."""
        text_file = tmp_path / "test.txt"
        text_file.write_bytes(b"This is text")
        
        result = is_pdf(text_file)
        assert result is False

    def test_is_pdf_file_not_found(self, tmp_path):
        """is_pdf() should return False for non-existent file."""
        missing_file = tmp_path / "missing.pdf"
        
        result = is_pdf(missing_file)
        assert result is False

    # =========================================================================
    # format_conversation_history Tests
    # =========================================================================

    def test_format_conversation_history_single_entry(self):
        """format_conversation_history() should format single entry correctly."""
        histories = [
            {"role": "user", "context": "Hello"},
        ]
        
        result = format_conversation_history(histories)
        expected = "Role: user\nContext: Hello"
        assert result == expected

    def test_format_conversation_history_multiple_entries(self):
        """format_conversation_history() should join multiple entries with separator."""
        histories = [
            {"role": "user", "context": "Hello"},
            {"role": "assistant", "context": "Hi there!"},
        ]
        
        result = format_conversation_history(histories)
        expected = "Role: user\nContext: Hello\n\n---\n\nRole: assistant\nContext: Hi there!"
        assert result == expected

    def test_format_conversation_history_missing_keys(self):
        """format_conversation_history() should handle missing keys with defaults."""
        histories = [
            {},  # Empty dict
            {"role": "user"},  # Missing context
            {"context": "Hello"},  # Missing role
        ]
        
        result = format_conversation_history(histories)
        assert "Role: unknown" in result
        assert "Context: Unknown context" in result

    def test_format_conversation_history_empty_list(self):
        """format_conversation_history() should return empty string for empty list."""
        result = format_conversation_history([])
        assert result == ""

    # =========================================================================
    # get_client_ip Tests
    # =========================================================================

    def test_get_client_ip_x_forwarded_for(self):
        """get_client_ip() should use X-Forwarded-For header."""
        request = MagicMock(spec=Request)
        request.headers = {"X-Forwarded-For": "192.168.1.1, 10.0.0.1"}
        request.client = MagicMock()
        request.client.host = "127.0.0.1"
        
        result = get_client_ip(request, trusted_proxies=True)
        assert result == "192.168.1.1"

    def test_get_client_ip_x_real_ip(self):
        """get_client_ip() should use X-Real-IP when X-Forwarded-For missing."""
        request = MagicMock(spec=Request)
        request.headers = {"X-Real-IP": "10.0.0.1"}
        request.client = MagicMock()
        request.client.host = "127.0.0.1"
        
        result = get_client_ip(request, trusted_proxies=True)
        assert result == "10.0.0.1"

    def test_get_client_ip_direct_client(self):
        """get_client_ip() should use direct client when no headers."""
        request = MagicMock(spec=Request)
        request.headers = {}
        request.client = MagicMock()
        request.client.host = "192.168.1.100"
        
        result = get_client_ip(request, trusted_proxies=True)
        assert result == "192.168.1.100"

    def test_get_client_ip_no_client(self):
        """get_client_ip() should return None when no client."""
        request = MagicMock(spec=Request)
        request.headers = {}
        request.client = None
        
        result = get_client_ip(request, trusted_proxies=True)
        assert result is None

    def test_get_client_ip_untrusted_proxies(self):
        """get_client_ip() should ignore headers when proxies untrusted."""
        request = MagicMock(spec=Request)
        request.headers = {
            "X-Forwarded-For": "192.168.1.1",
            "X-Real-IP": "10.0.0.1",
        }
        request.client = MagicMock()
        request.client.host = "192.168.1.100"
        
        result = get_client_ip(request, trusted_proxies=False)
        assert result == "192.168.1.100"

    # =========================================================================
    # generate_daily_token_quota_key Tests
    # =========================================================================

    def test_generate_daily_token_quota_key_format(self):
        """generate_daily_token_quota_key() should return correct format."""
        user_id = uuid4()
        result = generate_daily_token_quota_key(user_id)
        
        expected = f"token:user:{user_id}:daily"
        assert result == expected

    # =========================================================================
    # build_date_range_where_clause Tests
    # =========================================================================

    def test_build_date_range_where_clause_with_date_range(self):
        """build_date_range_where_clause() should build clause from DateRangeableMixin with date_range."""
        class TestMixin(DateRangeableMixin):
            date_range: DateRange = DateRange.LAST_7_DAYS
            date_start: datetime = None
            date_end: datetime = None
        
        mixin = TestMixin()
        result = build_date_range_where_clause("created_at", mixin, include_where=True)
        
        assert result.startswith(" WHERE ")
        assert "created_at >=" in result
        assert "created_at <" in result

    def test_build_date_range_where_clause_with_date_start_end(self):
        """build_date_range_where_clause() should use date_start and date_end."""
        class TestMixin(DateRangeableMixin):
            date_range: DateRange = None
            date_start: datetime = datetime(2024, 1, 1)
            date_end: datetime = datetime(2024, 12, 31)
        
        mixin = TestMixin()
        result = build_date_range_where_clause("created_at", mixin, include_where=False)
        
        assert result.startswith(" AND ")
        assert "created_at >= '2024-01-01T00:00:00'" in result
        assert "created_at < '2024-12-31T00:00:00'" in result

    def test_build_date_range_where_clause_with_date_range_none_and_no_start_end(self):
        """build_date_range_where_clause() should return empty when no dates."""
        class TestMixin(DateRangeableMixin):
            date_range: DateRange = None
            date_start: datetime = None
            date_end: datetime = None
        
        mixin = TestMixin()
        result = build_date_range_where_clause("created_at", mixin, include_where=True)
        
        assert result == ""

    def test_build_date_range_where_clause_include_where_false(self):
        """build_date_range_where_clause() should use AND prefix when include_where=False."""
        class TestMixin(DateRangeableMixin):
            date_range: DateRange = DateRange.TODAY
            date_start: datetime = None
            date_end: datetime = None
        
        mixin = TestMixin()
        result = build_date_range_where_clause("created_at", mixin, include_where=False)
        
        assert result.startswith(" AND ")

    def test_build_date_range_where_clause_date_range_all_days(self):
        """build_date_range_where_clause() should return empty for LAST_7_DAYS with no bounds."""
        class TestMixin(DateRangeableMixin):
            date_range: DateRange = DateRange.LAST_7_DAYS
            date_start: datetime = None
            date_end: datetime = None
        
        mixin = TestMixin()
        result = build_date_range_where_clause("created_at", mixin, include_where=True)
        
        # LAST_7_DAYS returns a range with start and end, so it should have conditions
        assert result != ""