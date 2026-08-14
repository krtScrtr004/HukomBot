from redis.asyncio import Redis
from backend.hukom_bot.exception.app_exception import RateLimitException


class RateLimiter:
    _SCRIPT = """
        local current = redis.call("INCR", KEYS[1])
        
        if current == 1 then
            redis.call("EXPIRE", KEYS[1], ARGV[1])
        end
        
        local remaining = tonumber(ARGV[2]) - current
        
        if remaining < 0 then
            remaining = 0
        end
        
        return {
            current,
            remaining, 
            redis.call("TTL", KEYS[1])
        }
        """

    def __init__(self, redis: Redis, limit: int = 10, window: int = 360):
        self._redis = redis
        self._limit = limit
        self._window = window

    async def __call__(self, key: str):
        # Register Lua script
        script = self._redis.register_script(self._SCRIPT)
        
        # Execute checks
        result = await script(
            keys=[key], args=[self._limit, self._window]
        )
        
        remaining = result[1]
        if remaining < 0:
            raise RateLimitException()