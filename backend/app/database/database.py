import os
from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row

from backend.app.core.settings import settings

class Database:
    _pool: AsyncConnectionPool | None = None

    def __init__(self):
        if Database._pool is None:
            DB_HOST = settings.DB_HOST
            DB_PORT = settings.DB_PORT
            DB_NAME = settings.DB_NAME
            DB_USER = settings.DB_USER
            DB_PASSWORD = settings.DB_PASSWORD

            if not all([DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD]):
                raise RuntimeError("Required database configuration missing")

            Database._pool = AsyncConnectionPool(
                conninfo=f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}",
                min_size=1,
                max_size=20,
                kwargs={"row_factory": dict_row},
                open=False,
            )

    async def open(self):
        await Database._pool.open()

    async def close(self):
        await Database._pool.close()

    def connection(self):
        """Returns an async context manager that automatically handles getconn/putconn"""
        return Database._pool.connection()