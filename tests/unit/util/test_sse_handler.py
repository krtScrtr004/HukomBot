import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import Request
from pydantic import BaseModel
from typing import Callable, Awaitable

from backend.hukom_bot.util.sse_handler import sse_handler
from backend.hukom_bot.service.pubsub_service import PubsubService


class TestSSEHandler:
    """Tests for sse_handler utility."""

    @pytest.fixture
    def mock_request(self):
        """Mock FastAPI Request."""
        request = MagicMock(spec=Request)
        request.is_disconnected = AsyncMock(return_value=False)
        return request

    @pytest.fixture
    def mock_pubsub_service(self):
        """Mock PubsubService."""
        service = MagicMock(spec=PubsubService)
        service.subscribe = AsyncMock()
        service.get_message = AsyncMock(return_value=None)
        service.unsubscribe = AsyncMock()
        service.close = AsyncMock()
        return service

    @pytest.fixture
    def mock_data_builder(self):
        """Mock data builder function."""
        class MockData(BaseModel):
            message: str = "test data"
        
        async def builder():
            return MockData()
        return builder

    # =========================================================================
    # sse_handler Tests
    # =========================================================================

    @pytest.mark.asyncio
    async def test_sse_handler_subscribes_on_start(
        self, mock_request, mock_pubsub_service, mock_data_builder
    ):
        """sse_handler() should subscribe to channel on start."""
        mock_pubsub_service.get_message.return_value = None  # Timeout immediately
        
        async def test():
            async for _ in sse_handler(
                request=mock_request,
                channel_name="test_channel",
                data_builder=mock_data_builder,
                pubsub_service=mock_pubsub_service,
                interval=0.1,
            ):
                break  # Exit after first iteration
        
        await test()
        mock_pubsub_service.subscribe.assert_called_once_with("test_channel")

    @pytest.mark.asyncio
    async def test_sse_handler_yields_heartbeat_on_timeout(
        self, mock_request, mock_pubsub_service, mock_data_builder
    ):
        """sse_handler() should yield heartbeat on timeout."""
        mock_pubsub_service.get_message.return_value = None
        
        async def test():
            async for message in sse_handler(
                request=mock_request,
                channel_name="test_channel",
                data_builder=mock_data_builder,
                pubsub_service=mock_pubsub_service,
                interval=0.1,
            ):
                if ": heartbeat" in message:
                    return message
            return None
        
        result = await test()
        assert ": heartbeat\n\n" in result

    @pytest.mark.asyncio
    async def test_sse_handler_yields_data_on_message(
        self, mock_request, mock_pubsub_service, mock_data_builder
    ):
        """sse_handler() should yield data when message received."""
        mock_pubsub_service.get_message.return_value = {"type": "message", "data": "test"}
        
        async def test():
            async for message in sse_handler(
                request=mock_request,
                channel_name="test_channel",
                data_builder=mock_data_builder,
                pubsub_service=mock_pubsub_service,
                interval=0.1,
            ):
                if "data:" in message:
                    return message
            return None
        
        result = await test()
        assert "data: " in result
        assert "test data" in result

    @pytest.mark.asyncio
    async def test_sse_handler_stops_on_disconnect(
        self, mock_request, mock_pubsub_service, mock_data_builder
    ):
        """sse_handler() should stop when request is disconnected."""
        mock_request.is_disconnected = AsyncMock(return_value=True)
        
        async def test():
            count = 0
            async for _ in sse_handler(
                request=mock_request,
                channel_name="test_channel",
                data_builder=mock_data_builder,
                pubsub_service=mock_pubsub_service,
                interval=0.1,
            ):
                count += 1
            return count
        
        count = await test()
        assert count == 0  # Should exit immediately

    @pytest.mark.asyncio
    async def test_sse_handler_unsubscribes_on_finally(
        self, mock_request, mock_pubsub_service, mock_data_builder
    ):
        """sse_handler() should unsubscribe and close on finally."""
        mock_pubsub_service.get_message.return_value = None
        
        async def test():
            async for _ in sse_handler(
                request=mock_request,
                channel_name="test_channel",
                data_builder=mock_data_builder,
                pubsub_service=mock_pubsub_service,
                interval=0.1,
            ):
                # Let it run through one full iteration (yield heartbeat)
                pass
        
        await test()
        
        mock_pubsub_service.unsubscribe.assert_called_once_with("test_channel")
        mock_pubsub_service.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_sse_handler_re_raises_cancelled_error(
        self, mock_request, mock_pubsub_service, mock_data_builder
    ):
        """sse_handler() should re-raise CancelledError."""
        mock_pubsub_service.get_message.side_effect = asyncio.CancelledError("test")
        
        with pytest.raises(asyncio.CancelledError):
            async for _ in sse_handler(
                request=mock_request,
                channel_name="test_channel",
                data_builder=mock_data_builder,
                pubsub_service=mock_pubsub_service,
                interval=0.1,
            ):
                pass

    @pytest.mark.asyncio
    async def test_sse_handler_cleans_up_on_exception(
        self, mock_request, mock_pubsub_service, mock_data_builder
    ):
        """sse_handler() should clean up on generic exception."""
        mock_pubsub_service.get_message.side_effect = Exception("Test error")
        
        with pytest.raises(Exception, match="Test error"):
            async for _ in sse_handler(
                request=mock_request,
                channel_name="test_channel",
                data_builder=mock_data_builder,
                pubsub_service=mock_pubsub_service,
                interval=0.1,
            ):
                pass
        
        # Should still clean up
        mock_pubsub_service.unsubscribe.assert_called_once_with("test_channel")
        mock_pubsub_service.close.assert_called_once()