from redis.asyncio import Redis
from backend.hukom_bot.exception.app_exception import RateLimitException

class RateLimiter:
    def __init__(self, 
        redis: Redis, 
        limit: int = 10, 
        window: int = 360
    ):
        self._redis = redis
        self._limit = limit
        self._window = window

    async def __call__(self, key: str):
        # Increment the counter for the given key
        current = await self._redis.incr(name=key, amount=1)
        
        # Set the expiration time for the key if it's the first request
        if current == 1:
            await self._redis.expire(name=key, time=self._window)
        
        # Check if the current count exceeds the limit
        if current >= self._limit:
            raise RateLimitException()