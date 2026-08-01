import ast
from psycopg import errors
from psycopg import AsyncConnection
from backend.app.database.database import Database
from backend.app.model.document_model import Document
from backend.app.model.chunk_model import Chunk
from backend.app.schema.chunk_schema import *
from backend.app.util.chunk_caster import ChunkCaster


class ChunkRepository:
    def __init__(self, db: Database):
        self._database = db

    async def create_many(
        self,
        chunks: list[ChunkCreate],
        connection: AsyncConnection = None,
    ) -> list[Chunk]:
        if not chunks:
            return []

        if connection is not None:
            return await self._create_many_implement(connection, chunks)

        async with self._database.connection() as conn:
            try:
                result = await self._create_many_implement(conn, chunks)
                await conn.commit()
                return result
            except (
                errors.ForeignKeyViolation,
                errors.IntegrityError,
                errors.OperationalError,
            ) as ex:
                await conn.rollback()
                raise

    async def _create_many_implement(
        self,
        conn: AsyncConnection,
        chunks: list[ChunkCreate],
    ) -> list[Chunk]:
        async with conn.cursor() as cur:
            await cur.executemany(
                """
                INSERT INTO chunks (
                    id,
                    document_id, 
                    chunk_number, 
                    chunk_text, 
                    embedding, 
                    section
                ) VALUES (
                    %(id)s,
                    %(document_id)s, 
                    %(chunk_number)s, 
                    %(chunk_text)s, 
                    %(embedding)s, 
                    %(section)s
                )
                """,
                [chunk.model_dump() for chunk in chunks],
            )

            updated = []
            for i, _ in enumerate(chunks):
                updated.append(ChunkCaster.create_to_base(chunks[i]))

        return updated

    async def search(
        self, chunk: ChunkSearchKeyword, connection: AsyncConnection = None
    ) -> list:
        if connection is not None:
            return await self._search_implement(connection, chunk)

        async with self._database.connection() as conn:
            try:
                result = await self._search_implement(conn, chunk)
                await conn.commit()
                return result
            except errors.OperationalError as ex:
                print(f"DB error: {ex}")
                await conn.rollback()
                raise

    async def _search_implement(self, conn: AsyncConnection, chunk: ChunkSearchKeyword):
        async with conn.cursor() as cur:
            await cur.execute(
                """
                WITH query AS (
                    SELECT plainto_tsquery('english', %s) AS q
                )
                SELECT
                    -- Chunk Info
                    c.id AS c_id,
                    c.chunk_number AS c_chunk_number,
                    c.chunk_text AS c_chunk_text,
                    c.embedding AS c_embedding,
                    c.section AS c_section,
                    ts_rank(c.search_vector, q.q) AS c_rank,

                    -- Document Info
                    d.id AS d_id,
                    d.uploader_id AS d_uploader_id,
                    d.original_file_name AS d_original_file_name,
                    d.upload_file_name AS d_upload_file_name,
                    d.document_type AS d_document_type,
                    d.file_type AS d_file_type,
                    d.upload_status AS d_upload_status,
                    d.upload_error AS d_upload_error,
                    d.digest AS d_digest,
                    d.created_at AS d_created_at
                FROM chunks c
                JOIN documents d ON c.document_id = d.id
                CROSS JOIN query q
                WHERE c.search_vector @@ q.q
                ORDER BY c_rank DESC
                LIMIT %s
                OFFSET %s
                """,
                (chunk.text, chunk.limit, chunk.offset),
            )

            rows = await cur.fetchall()

        chunks = []
        for row in rows:
            chunk = Chunk(
                id=row["c_id"],
                document_id=row["d_id"],
                chunk_number=int(row["c_chunk_number"]),
                chunk_text=row["c_chunk_text"],
                embedding=ast.literal_eval(row["c_embedding"]),
                section=row["c_section"],
                # Document Prop
                document=Document(
                    id=row["d_id"],
                    uploader_id=row["d_uploader_id"],
                    original_file_name=row["d_original_file_name"],
                    upload_file_name=row["d_upload_file_name"],
                    document_type=row["d_document_type"],
                    file_type=row["d_file_type"],
                    upload_status=row["d_upload_status"],
                    upload_error=row["d_upload_error"],
                    digest=row["d_digest"],
                    created_at=row["d_created_at"],
                ),
            )
            chunks.append(chunk)

        return chunks

    async def search_vector(
        self, chunk: ChunkSearchVector, connection: AsyncConnection = None
    ) -> list[Chunk]:
        if connection is not None:
            return await self._search_vector_implement(connection, chunk)

        async with self._database.connection() as conn:
            try:
                result = await self._search_vector_implement(conn, chunk)
                await conn.commit()
                return result
            except errors.OperationalError as ex:
                print(f"DB error: {ex}")
                await conn.rollback()
                raise

    async def _search_vector_implement(
        self, conn: AsyncConnection, chunk: ChunkSearchVector
    ):
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT 
                    -- Chunk Info
                    c.id as c_id,
                    c.chunk_number as c_chunk_number,
                    c.chunk_text as c_chunk_text,
                    c.embedding as c_embedding,
                    c.section as c_section,

                    -- Document Info
                    d.id AS d_id,
                    d.uploader_id AS d_uploader_id,
                    d.original_file_name AS d_original_file_name,
                    d.upload_file_name AS d_upload_file_name,
                    d.document_type AS d_document_type,
                    d.file_type AS d_file_type,
                    d.upload_status AS d_upload_status,
                    d.upload_error AS d_upload_error,
                    d.digest AS d_digest,
                    d.created_at AS d_created_at
                FROM chunks c
                JOIN documents d
                    ON c.document_id = d.id
                ORDER BY c.embedding <=> %s::vector
                LIMIT %s
                OFFSET %s
                """,
                (str(chunk.embeddings), chunk.limit, chunk.offset),
            )

            rows = await cur.fetchall()

        chunks = []
        for row in rows:
            chunk = Chunk(
                id=row["c_id"],
                document_id=row["d_id"],
                chunk_number=int(row["c_chunk_number"]),
                chunk_text=row["c_chunk_text"],
                embedding=ast.literal_eval(row["c_embedding"]),
                section=row["c_section"],
                # Document Prop
                document=Document(
                    id=row["d_id"],
                    uploader_id=row["d_uploader_id"],
                    original_file_name=row["d_original_file_name"],
                    upload_file_name=row["d_upload_file_name"],
                    document_type=row["d_document_type"],
                    file_type=row["d_file_type"],
                    upload_status=row["d_upload_status"],
                    upload_error=row["d_upload_error"],
                    digest=row["d_digest"],
                    created_at=row["d_created_at"],
                ),
            )
            chunks.append(chunk)

        return chunks
