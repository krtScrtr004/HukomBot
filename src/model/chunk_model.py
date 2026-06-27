from __future__ import annotations
from uuid import UUID
from typing import List, Dict, Optional
from model.model import Model
from model.document_model import DocumentModel
from datetime import datetime
from psycopg import errors


class ChunkModel(Model):
    def __init__(
        self,
        id: UUID = None,
        document_id: UUID = None,
        chunk_number: int = None,
        chunk_text: str = None,
        section: str = None,
        embedding: list = None,
        document: DocumentModel = None,
    ):
        super().__init__()

        self.id = id
        self.document_id = document_id
        self.chunk_number = chunk_number
        self.chunk_text = chunk_text
        self.section = section
        self.embedding = embedding

        self.document = document  # Navigation prop

    def create(self):
        if not self.document_id:
            raise RuntimeError("Document Id not provided")
        if not self.chunk_number:
            raise RuntimeError("Chunk number not provided")
        if not self.chunk_text:
            raise RuntimeError("Chunk text not provided")
        if not self.embedding:
            raise RuntimeError("Embeddings not provided")
        if not self.section:
            raise RuntimeError("Section not provided")

        with self.connection.connection() as conn:
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
                            self.document_id,
                            self.chunk_number,
                            self.chunk_text,
                            self.embedding,
                            self.section,
                        ),
                    )

                    # Set chunk id
                    self.id = cur.fetchone()[0]

                conn.commit()
            except errors.IntegrityError as ex:
                print(f"Integrity error exception: {ex}")
                conn.rollback()
            except errors.ForeignKeyViolation as ex:
                print(f"Document id not found exception: {ex}")
                conn.rollback()
            except errors.OperationalError as ex:
                print(f"Insert error: {ex}")
                raise

    def search(self, chunk_text: str, limit: int = 10, offset: int = 0):
        with self.connection.connection() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        f"""
                        WITH query AS (
                            SELECT plainto_tsquery('english', %s) as q
                        )
                        SELECT
                            c.id as c_id,
                            c.chunk_number as c_chunk_number,
                            c.chunk_text as c_chunk_text,
                            c.embedding as c_embedding,
                            c.section as c_section,
                            ts_rank(c.search_vector, q.q) as c_rank,
                            d.id as d_id,
                            d.title as d_title,
                            d.file_type as d_file_type
                        FROM chunks c, query q
                        JOIN document d
                            ON c.document_id = d.id
                        WHERE c.search_vector @@ q.q
                        ORDER BY c_rank DESC
                        LIMIT {limit}
                        OFFSET {offset}
                        """,
                        (chunk_text,),
                    )

                    rows = cur.fetchall()

                    chunks = []
                    for row in rows:
                        chunk = ChunkModel(
                            id=UUID(row["c_id"]),
                            document_id=UUID(row["d_id"]),
                            chunk_number=int(row["c_chunk_number"]),
                            chunk_text=row["c_chunk_text"],
                            embedding=row["c_embedding"],
                            section=row["c_section"],
                            document=DocumentModel(
                                id=row["d_id"],
                                title=row["d_title"],
                                file_type=row["d_file_type"],
                            ),
                        )
                        chunks.append(chunk)

                    return chunks
            except errors.OperationalError as ex:
                print(f"Insert error: {ex}")
                raise

    def search_vector(self, chunk_embedding: list, limit: int = 10, offset: int = 0):
        with self.connection.connection() as conn:
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
                            d.file_type as d_file_type
                        FROM chunks c
                        JOIN documents d
                            ON c.document_id = d.id
                        ORDER BY c.embedding <=> %s
                        LIMIT %s
                        OFFSET %s
                        """,
                        (chunk_embedding, limit, offset),
                    )

                    rows = cur.fetchall()

                    chunks = []
                    for row in rows:
                        chunk = ChunkModel(
                            id=UUID(row["c_id"]),
                            document_id=UUID(row["d_id"]),
                            chunk_number=int(row["c_chunk_number"]),
                            chunk_text=row["c_chunk_text"],
                            embedding=row["c_embedding"],
                            section=row["c_section"],
                            document=DocumentModel(
                                id=row["d_id"],
                                title=row["d_title"],
                                file_type=row["d_file_type"],
                            ),
                        )
                        chunks.append(chunk)

                    return chunks
            except errors.OperationalError as ex:
                print(f"Insert error: {ex}")
                raise

    @staticmethod
    def create_many(chunks: List[ChunkModel]):
        if not chunks:
            return

        model = ChunkModel()

        params = []
        for chunk in chunks:
            entry = {}
            if not chunk.document_id:
                raise RuntimeError("Document Id not provided")
            entry["document_id"] = chunk.document_id
            if chunk.chunk_number < 0:
                raise RuntimeError("Chunk number not provided")
            entry["chunk_number"] = chunk.chunk_number
            if not chunk.chunk_text:
                raise RuntimeError("Chunk text not provided")
            entry["chunk_text"] = chunk.chunk_text
            if not all(chunk.embedding):
                raise RuntimeError("Embeddings not provided")
            entry["embedding"] = chunk.embedding
            if not chunk.section:
                raise RuntimeError("Section not provided")
            entry["section"] = chunk.section
            params.append(entry)

        with model.connection.connection() as conn:
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
                                param["document_id"],
                                param["chunk_number"],
                                param["chunk_text"],
                                param["embedding"],
                                param["section"],
                            )
                            for param in params
                        ],
                        returning=True,
                    )

                    # Retrieve the generated IDs
                    counter = 0
                    while True:
                        row = cur.fetchone()
                        if row:
                            # Update the chunk's ID attribute
                            chunks[counter].id = row[0]
                            counter += 1
                        if not cur.nextset():
                            break

                conn.commit()
            except errors.IntegrityError as ex:
                print(f"Integrity error exception: {ex}")
                conn.rollback()
            except errors.ForeignKeyViolation as ex:
                print(f"Document id not found exception: {ex}")
                conn.rollback()
            except errors.OperationalError as ex:
                print(f"Insert error: {ex}")
                raise
