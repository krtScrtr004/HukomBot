# src/database/database.py
import os
import psycopg
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()


class Database:
    _pool = None

    def __init__(self):
        if Database._pool is None:
            DB_HOST = os.getenv("DB_HOST")
            DB_PORT = os.getenv("DB_PORT")
            DB_NAME = os.getenv("DB_NAME")
            DB_USER = os.getenv("DB_USER")
            DB_PASSWORD = os.getenv("DB_PASSWORD")

            if not all([DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD]):
                raise RuntimeError("Required database configuration missing")

            Database._pool = ConnectionPool(
                conninfo=f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}",
                min_size=1,
                max_size=20,
                kwargs={"row_factory": dict_row},
            )

    def connection(self):
        """Returns a context manager that automatically handles getconn/putconn"""
        return self._pool.connection()
