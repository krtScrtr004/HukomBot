import pytest
import pytest_asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Any

from backend.hukom_bot.service.pubsub_service import PubsubService


class TestPubsubService:
    """Tests for PubsubService methods."""

    @pytest.fixture
    def mock_redis(self):
        """Mock Redis client."""
        return MagicMock()

    @pytest.fixture
    def mock_pubsub(self):
        """Mock Redis PubSub."""
        pubsub = AsyncMock()
        pubsub.subscribe = AsyncMock()
        pubsub.unsubscribe = AsyncMock()
        pubsub.get_message = AsyncMock(return_value=None)
        pubsub.close = AsyncMock()
        return pubsub

    @pytest.fixture
    def pubsub_service(self, mock_redis, mock_pubsub):
        """Create PubsubService instance with mocked dependencies."""
        service = PubsubService(redis=mock_redis)
        service._pubsub = mock_pubsub
        return service

    # =========================================================================
    # Subscribe Tests
    # =========================================================================

    @pytest.mark.asyncio
    async def test_subscribe_single_channel(self, pubsub_service, mock_pubsub):
        """subscribe() should subscribe to a single channel."""
        await pubsub_service.subscribe("test_channel")

        mock_pubsub.subscribe.assert_called_once_with("test_channel")

    @pytest.mark.asyncio
    async def test_subscribe_multiple_channels(self, pubsub_service, mock_pubsub):
        """subscribe() should subscribe to multiple channels."""
        await pubsub_service.subscribe("channel1", "channel2", "channel3")

        mock_pubsub.subscribe.assert_called_once_with("channel1", "channel2", "channel3")

    # =========================================================================
    # Publish Tests
    # =========================================================================

    @pytest.mark.asyncio
    async def test_publish_returns_message_count(self, pubsub_service, mock_redis):
        """publish() should return number of subscribers who received the message."""
        mock_redis.publish = AsyncMock(return_value=3)

        result = await pubsub_service.publish("test_channel", {"data": "test"})

        assert result == 3
        mock_redis.publish.assert_called_once()
        call_args = mock_redis.publish.call_args
        assert call_args[1]["channel"] == "test_channel"
        # Data should be JSON serialized
        expected_data = json.dumps({"data": "test"})
        assert call_args[1]["message"] == expected_data

    @pytest.mark.asyncio
    async def test_publish_serializes_data_as_json(self, pubsub_service, mock_redis):
        """publish() should serialize data as JSON."""
        mock_redis.publish = AsyncMock(return_value=1)

        test_data = {"key": "value", "number": 42}
        await pubsub_service.publish("test_channel", test_data)

        call_args = mock_redis.publish.call_args
        expected_json = json.dumps(test_data)
        assert call_args[1]["message"] == expected_json

    # =========================================================================
    # Get Message Tests
    # =========================================================================

    @pytest.mark.asyncio
    async def test_get_message_returns_none_on_timeout(self, pubsub_service, mock_pubsub):
        """get_message() should return None when timeout occurs."""
        mock_pubsub.get_message.return_value = None

        result = await pubsub_service.get_message(timeout=0.1)

        assert result is None
        mock_pubsub.get_message.assert_called_once_with(ignore_subscribe_messages=False, timeout=0.1)

    @pytest.mark.asyncio
    async def test_get_message_returns_message_when_available(self, pubsub_service, mock_pubsub):
        """get_message() should return message when available."""
        expected_msg = {"type": "message", "channel": "test", "data": '{"data": "test"}'}
        mock_pubsub.get_message.return_value = expected_msg

        result = await pubsub_service.get_message(timeout=1.0)

        assert result == expected_msg

    @pytest.mark.asyncio
    async def test_get_message_ignore_subscribe_messages(self, pubsub_service, mock_pubsub):
        """get_message() should pass ignore_subscribe_messages parameter."""
        mock_pubsub.get_message.return_value = None

        await pubsub_service.get_message(ignore_subscribe_messages=True, timeout=0.5)

        mock_pubsub.get_message.assert_called_once_with(ignore_subscribe_messages=True, timeout=0.5)

    # =========================================================================
    # Unsubscribe Tests
    # =========================================================================

    @pytest.mark.asyncio
    async def test_unsubscribe_single_channel(self, pubsub_service, mock_pubsub):
        """unsubscribe() should unsubscribe from a single channel."""
        await pubsub_service.unsubscribe("test_channel")

        mock_pubsub.unsubscribe.assert_called_once_with("test_channel")

    @pytest.mark.asyncio
    async def test_unsubscribe_multiple_channels(self, pubsub_service, mock_pubsub):
        """unsubscribe() should unsubscribe from multiple channels."""
        await pubsub_service.unsubscribe("channel1", "channel2")

        mock_pubsub.unsubscribe.assert_called_once_with("channel1", "channel2")

    # =========================================================================
    # Close Tests
    # =========================================================================

    @pytest.mark.asyncio
    async def test_close_closes_pubsub(self, pubsub_service, mock_pubsub):
        """close() should close the pubsub connection."""
        await pubsub_service.close()

        mock_pubsub.close.assert_called_once()