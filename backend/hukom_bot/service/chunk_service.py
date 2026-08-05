import asyncio
from pathlib import Path
from psycopg import AsyncConnection
from fastapi.concurrency import run_in_threadpool

from backend.hukom_bot.schema.chunk_schema import *
from backend.hukom_bot.repository.chunk_repository import ChunkRepository
from backend.hukom_bot.exception.chunk_exception import ChunkFileException

from backend.hukom_bot.util.extract_text_from_pdf import extract_text_from_pdf

ocr_semaphor = asyncio.Semaphore(
    1
)  # Allow only 1 OCR process to use GPU at the same time


class ChunkService:
    def __init__(self, chunk_repo: ChunkRepository):
        self._chunk_repo = chunk_repo

    # Repository =================

    async def create_many(
        self, chunks: list[ChunkCreate], connection: AsyncConnection = None
    ):
        return await self._chunk_repo.create_many(chunks, connection)

    async def search_vector(
        self, chunk: ChunkSearchVector, connection: AsyncConnection = None
    ):
        return await self._chunk_repo.search_vector(chunk, connection)
    
    async def search_keyword(
        self, chunk: ChunkSearchKeyword, connection: AsyncConnection = None
    ):
        return await self._chunk_repo.search(chunk, connection)

    # Others ======================

    async def extract_text_to_chunks(self, file: Path):
        async with ocr_semaphor:
            chunks = await run_in_threadpool(extract_text_from_pdf, file)
            if not chunks:
                raise ChunkFileException("No chunks extracted from file")

            return chunks
