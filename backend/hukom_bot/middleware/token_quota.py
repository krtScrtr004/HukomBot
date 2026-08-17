from redis.asyncio import Redis
from backend.hukom_bot.exception.app_exception import RateLimitException


class TokenQuota:
    def __init__(self, redis: Redis, daily_quota: int, daily_window: int):
        self._redis = redis
        self._daily_quota = daily_quota
        self._daily_window = daily_window

    async def reserve_token(self, key: str, estimated_token: int):
        script = self._redis.register_script("""
            -- KEYS[1] = daily quota key
    
            -- ARGV[1] = estimated tokens to reserve
            -- ARGV[2] = daily token quota
            -- ARGV[3] = daily key TTL
    
            local key = KEYS[1]
    
            local estimated_tokens = tonumber(ARGV[1])
            local daily_quota = tonumber(ARGV[2])
    
            local daily_ttl = tonumber(ARGV[3])
    
            -- Get current daily usage
            local daily_used = tonumber(redis.call("HGET", key, "used") or "0")
            local daily_reserved = tonumber(redis.call("HGET", key, "reserved") or "0")
            local daily_remaining_ttl = tonumber(redis.call("TTL", key) or 0)
    
            -- Calculate remaining available quota
            local daily_remaining =
                daily_quota - daily_used - daily_reserved
    
            -- Check daily quota
            if estimated_tokens > daily_remaining then
                return {
                    0,
                    daily_remaining,
                    daily_remaining_ttl
                }
            end
    
            -- Reserve tokens
            redis.call(
                "HINCRBY",
                key,
                "reserved",
                estimated_tokens
            )
    
            -- Set expiration for newly created keys
            if redis.call("TTL", key) == -1 then
                redis.call("EXPIRE", key, daily_ttl)
            end
    
            -- Return successful reservation
            return {
                1,
                daily_remaining - estimated_tokens,
                daily_remaining_ttl
            }
            """)

        response = await script(
            keys=[key], args=[estimated_token, self._daily_quota, self._daily_window]
        )

        result = response[0]
        remaining = response[1]
        remaining_ttl = response[2]

        if not result or remaining < 0:
            raise RateLimitException(
                headers={"Retry-At": f"{remaining_ttl}s"},
                code="TOKEN_QUOTA_ERROR",
                message="Insufficient remaing tokens",
            )

    async def reconcile_token(self, key: str, actual_tokens_used: int):
        script = self._redis.register_script("""
            -- KEYS[1] = key
            
            -- ARGS[1] = daily_quota
            -- ARGS[2] = actual token used
            
            local key = KEYS[1]

            local daily_quota = tonumber(ARGV[1])
            local actual_tokens = tonumber(ARGV[2])

            local used = tonumber(
                redis.call("HGET", key, "used") or "0"
            )

            local reserved_tokens = tonumber(
                redis.call("HGET", key, "reserved") or "0"
            )

            -- Validate input
            if actual_tokens < 0 then
                return {
                    0,
                    "invalid_actual_tokens"
                }
            end

            if reserved_tokens < 0 then
                return {
                    0,
                    "invalid_reserved_tokens"
                }
            end

            -- Record actual usage
            redis.call(
                "HINCRBY",
                key,
                "used",
                actual_tokens
            )

            -- Release this operation's reservation
            redis.call(
                "HINCRBY",
                key,
                "reserved",
                -reserved_tokens
            )

            -- Calculate remaining quota
            local new_used = used + actual_tokens
            local remaining = daily_quota - new_used

            return {
                1,
                remaining
            }
            """)

        await script(keys=[key], args=[self._daily_quota, actual_tokens_used])
