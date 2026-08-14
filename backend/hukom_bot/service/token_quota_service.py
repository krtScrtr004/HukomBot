from redis.asyncio import Redis
from backend.hukom_bot.core.settings import settings
from backend.hukom_bot.middleware.token_quota import TokenQuota


class TokenQuotaService:
    def __init__(
        self,
        redis: Redis,
        daily_quota: int = settings.TOKEN_QUOTA_DAILY,
        daily_window: int = settings.TOKEN_QUOTA_WINDOW,
    ):
        self._middleware = TokenQuota(
            redis=redis, daily_quota=daily_quota, daily_window=daily_window
        )

    async def reserve_token(self, key: str, estimated_token: int):
        await self._middleware.reserve_token(key=key, estimated_token=estimated_token)

    async def reconcile_token(self, key: str, actual_tokens_used: int):
        await self._middleware.reconcile_token(
            key=key, actual_tokens_used=actual_tokens_used
        )
