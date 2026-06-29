from database.database import Database
from model.document_model import Document
from model.chunk_model import Chunk, ChunkCreate, ChunkSearchKeyword, ChunkSearchVector
from typing import List
from psycopg import errors
from datetime import datetime


class ChunkRepository:
    def __init__(self):
        self.database = Database()

    def create(self, chunk: ChunkCreate) -> Chunk:
        with self.database.connection() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO chunks (
                            document_id, chunk_number, chunk_text, embedding, section
                        ) VALUES (
                            %s, %s, %s, %s, %s
                        ) RETURNING id
                        """,
                        (
                            chunk.document_id,
                            chunk.chunk_number,
                            chunk.chunk_text,
                            chunk.embedding,
                            chunk.section,
                        ),
                    )

                    chunk_id = cur.fetchone()[0]

                conn.commit()
            except (
                errors.ForeignKeyViolation,
                errors.IntegrityError,
                errors.OperationalError,
            ) as ex:
                print(f"DB Error: {ex}")
                conn.rollback()
                raise

        return Chunk(
            id=chunk_id,
            document_id=chunk.document_id,
            chunk_number=chunk.chunk_number,
            chunk_text=chunk.chunk_text,
            section=chunk.section,
            embedding=chunk.embedding,
        )

    def create_many(self, chunks: List[ChunkCreate]) -> List[Chunk]:
        if not chunks:
            return

        with self.database.connection() as conn:
            try:
                with conn.cursor() as cur:
                    cur.executemany(
                        """
                        INSERT INTO chunks (
                            document_id, chunk_number, chunk_text, embedding, section
                        ) VALUES (
                            %s, %s, %s, %s, %s
                        ) RETURNING id
                        """,
                        [
                            (
                                chunk.document_id,
                                chunk.chunk_number,
                                chunk.chunk_text,
                                chunk.embedding,
                                chunk.section,
                            )
                            for chunk in chunks
                        ],
                        returning=True,
                    )

                    updated = []
                    counter = 0
                    while True:
                        row = cur.fetchone()
                        if row:
                            updated.extend(
                                Chunk(
                                    id=row[0],
                                    document_id=chunks[counter].document_id,
                                    chunk_number=chunks[counter].chunk_number,
                                    chunk_text=chunks[counter].chunk_text,
                                    section=chunks[counter].section,
                                    embedding=chunks[counter].embedding,
                                )
                            )
                            counter += 1
                        if not cur.nextset():
                            break

                conn.commit()
                return updated
            except (
                errors.ForeignKeyViolation,
                errors.IntegrityError,
                errors.OperationalError,
            ) as ex:
                print(f"DB Error: {ex}")
                conn.rollback()
                raise

    def search(self, chunk: ChunkSearchKeyword) -> List:
        with self.database.connection() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        WITH query AS (
                            SELECT plainto_tsquery('english', %s) AS q
                        )
                        SELECT
                            c.id AS c_id,
                            c.chunk_number AS c_chunk_number,
                            c.chunk_text AS c_chunk_text,
                            c.embedding AS c_embedding,
                            c.section AS c_section,
                            ts_rank(c.search_vector, q.q) AS c_rank,
                            d.id AS d_id,
                            d.title AS d_title,
                            d.file_type AS d_file_type,
                            d.created_at AS d_created_at
                        FROM chunks c
                        JOIN documents d ON c.document_id = d.id
                        CROSS JOIN query q
                        WHERE c.search_vector @@ q.q
                        ORDER BY c_rank DESC
                        LIMIT %s
                        OFFSET %s
                        """,
                        (chunk.chunk_text, chunk.limit, chunk.offset),
                    )

                    rows = cur.fetchall()

                    chunks = []
                    for row in rows:
                        chunk = Chunk(
                            id=row["c_id"],
                            document_id=row["d_id"],
                            chunk_number=int(row["c_chunk_number"]),
                            chunk_text=row["c_chunk_text"],
                            embedding=row["c_embedding"],
                            section=row["c_section"],
                            document=Document(
                                id=row["d_id"],
                                title=row["d_title"],
                                file_type=row["d_file_type"],
                                created_at=datetime.fromisoformat(row["d_created_at"]),
                            ),
                        )
                        chunks.append(chunk)

                    return chunks
            except errors.OperationalError as ex:
                print(f"DB error: {ex}")
                raise

    def search_vector(self, chunk: ChunkSearchVector) -> List[Chunk]:
        with self.database.connection() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT 
                            c.id as c_id,
                            c.chunk_number as c_chunk_number,
                            c.chunk_text as c_chunk_text,
                            c.embedding as c_embedding,
                            c.section as c_section,
                            d.id as d_id,
                            d.title as d_title,
                            d.file_type as d_file_type,
                            d.created_at as d_created_at
                        FROM chunks c
                        JOIN documents d
                            ON c.document_id = d.id
                        ORDER BY c.embedding <=> %s::vector
                        LIMIT %s
                        OFFSET %s
                        """,
                        (str(chunk.embeddings), chunk.limit, chunk.offset),
                    )

                    rows = cur.fetchall()

                    chunks = []
                    for row in rows:
                        chunk = Chunk(
                            id=row["c_id"],
                            document_id=row["d_id"],
                            chunk_number=int(row["c_chunk_number"]),
                            chunk_text=row["c_chunk_text"],
                            embedding=row["c_embedding"],
                            section=row["c_section"],
                            document=Document(
                                id=row["d_id"],
                                title=row["d_title"],
                                file_type=row["d_file_type"],
                                created_at=datetime.fromisoformat(row["d_created_at"])
                            ),
                        )
                        chunks.append(chunk)

                    return chunks
            except errors.OperationalError as ex:
                print(f"DB error: {ex}")
                raise
