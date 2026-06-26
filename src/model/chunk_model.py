from __future__ import annotations
import uuid
from typing import List, Dict, Optional
from model.model import Model
from datetime import datetime
from psycopg import errors


class ChunkModel(Model):
    def __init__(
        self,
        id: uuid = None,
        document_id: uuid = None,
        chunk_number: int = None,
        chunk_text: str = None,
        embedding: list = None,
    ):
        super().__init__()

        self.id = id
        self.document_id = document_id
        self.chunk_number = chunk_number
        self.chunk_text = chunk_text
        self.embedding = embedding

    def create(self):
        if not self.document_id:
            raise RuntimeError("Document Id not provided")
        if not self.chunk_number:
            raise RuntimeError("Chunk number not provided")
        if not self.chunk_text:
            raise RuntimeError("Chunk text not provided")
        if not self.embedding:
            raise RuntimeError("Embeddings not provided")

        with self.connection.connection() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO chunks (
                            document_id, chunk_number, chunk_text, embedding
                        ) VALUES (
                            %s, %s, %s, %s
                        ) RETURNING id
                        """,
                        (
                            self.document_id,
                            self.chunk_number,
                            self.chunk_text,
                            self.embedding,
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

    def search(self, chunk_text: str):
        with self.connection.connection() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        WITH query AS (
                            SELECT plainto_tsquery('english', %s) as q
                        )
                        SELECT
                            c.*,
                            ts_rank(
                                c.search_vector, q.q
                            ) as rank
                        FROM chunks c, query q
                        WHERE search_vector @@ q.q
                        ORDER BY rank DESC
                        """,
                        (chunk_text,),
                    )

                    rows = cur.fetchall()

                    chunks = []
                    for row in rows:
                        chunk = ChunkModel(
                            id=uuid.UUID(row["id"]),
                            document_id=uuid.UUID(row["document_id"]),
                            chunk_number=int(row["chunk_id"]),
                            chunk_text=row["chunk_text"],
                            embedding=row["embedding"],
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
            params.append(entry)

        with model.connection.connection() as conn:
            try:
                with conn.cursor() as cur:
                    cur.executemany(
                        """
                        INSERT INTO chunks (
                            document_id, chunk_number, chunk_text, embedding
                        ) VALUES (
                            %s, %s, %s, %s
                        ) RETURNING id
                        """,
                        [
                            (
                                param["document_id"],
                                param["chunk_number"],
                                param["chunk_text"],
                                param["embedding"],
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