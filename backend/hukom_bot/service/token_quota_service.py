from uuid import UUID
from redis.asyncio import Redis
from backend.hukom_bot.core.settings import settings
from backend.hukom_bot.middleware.token_quota import TokenQuota
from backend.hukom_bot.schema.auth_schema import TokenQuotaUsage
from backend.hukom_bot.util.utility import generate_daily_token_quota_key


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

    async def retrieve_usage(self, user_id: UUID) -> TokenQuotaUsage:
        return await self._middleware.retrieve_usage(
            key=generate_daily_token_quota_key(user_id)
        )
