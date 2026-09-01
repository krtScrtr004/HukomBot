from __future__ import annotations

import json
from redis.asyncio import Redis


class PubsubService:
    def __init__(self, redis: Redis):
        self._redis = redis
        self._pubsub = redis.pubsub()

    async def subscribe(self, *channels):
        await self._pubsub.subscribe(channels)

    async def publish(self, channel: str, data: any) -> int:
        return await self._redis.publish(channel=channel, message=json.dumps(data))

    async def get_message(
        self, ignore_subscribe_messages: bool = False, timeout: float | None = 0
    ) -> str | None:
        return await self._pubsub.get_message(
            ignore_subscribe_messages=ignore_subscribe_messages, timeout=timeout
        )

    async def unsubscribe(self, *channels):
        await self._pubsub.unsubscribe(channels)

    async def close(self):
        await self._pubsub.close()
