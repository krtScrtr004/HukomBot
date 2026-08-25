from __future__ import annotations
from redis.asyncio import Redis, ConnectionPool

from backend.hukom_bot.core.settings import settings

_client: Redis | None = None
_pool: ConnectionPool | None = None

def get_redis(
    host: str = settings.REDIS_HOST,
    port: int = settings.REDIS_PORT,
    max_connections: int = 20
) -> Redis:
    global _client, _pool
    
    # Initialize redis connection pool
    if not _client:
        _pool =  ConnectionPool(
            host=host,
            port=port,
            max_connections=max_connections,
            decode_responses=True
        )
        
        _client = Redis(connection_pool=_pool)

    return _client

async def close_redis() -> None:
    global _client, _pool

    if _client is not None:
        await _client.aclose()
        await _pool.aclose()
        
        _client = None
        _pool = None