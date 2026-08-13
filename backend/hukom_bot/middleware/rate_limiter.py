from redis import Redis
from fastapi import HTTPException

from backend.hukom_bot.exception.rate_limit_exeception import RateLimitException


class RateLimiter:
    def __init__(self, 
        redis: Redis, 
        limit: int = 10, 
        window: int = 360
    ):
        self._redis = redis
        self._limit = limit
        self._window = window

    def __call__(self, key: str):
        # Increment the counter for the given key
        current = self._redis.incr(1)
        
        # Set the expiration time for the key if it's the first request
        if current == 1:
            self._redis.expire(name=key, time=self._window)
        
        # Check if the current count exceeds the limit
        if current >= self._limit:
            raise RateLimitException()