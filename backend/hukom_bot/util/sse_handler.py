import asyncio
import logging
from fastapi import Request
from pydantic import BaseModel
from typing import Callable, Awaitable
from backend.hukom_bot.service.pubsub_service import PubsubService

logger = logging.getLogger(__name__)


async def sse_handler(
    request: Request,
    channel_name: str,
    data_builder: Callable[[], Awaitable[BaseModel]],
    pubsub_service: PubsubService,
    interval: float = 15.0,
):
    await pubsub_service.subscribe(channel_name)

    try:
        while True:
            if await request.is_disconnected():
                break

            message = await pubsub_service.get_message(
                ignore_subscribe_messages=True, timeout=interval
            )

            if message is None:
                yield ": heartbeat\n\n"
                continue

            data = await data_builder()
            yield f"data: {data.model_dump_json()}\n\n"
    except asyncio.CancelledError:
        logger.info(
            "SSE cancelled on channel=%s",
            channel_name,
        )
        raise
    except Exception as ex:
        raise
    finally:
        await pubsub_service.unsubscribe(channel_name)
        await pubsub_service.close()
