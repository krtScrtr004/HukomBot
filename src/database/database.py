import os
import psycopg
from dotenv import load_dotenv

load_dotenv()


class Database:
    def __init__(self):
        DB_HOST = os.getenv("DB_HOST")
        DB_PORT = os.getenv("DB_PORT")
        DB_NAME = os.getenv("DB_NAME")
        DB_USER = os.getenv("DB_USER")
        DB_PASSWORD = os.getenv("DB_PASSWORD")

        if not DB_HOST or not DB_PORT or not DB_NAME or not DB_USER or not DB_PASSWORD:
            raise RuntimeError("Required database configuration missing")

        self.conn = psycopg.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
        )
