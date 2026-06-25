import uuid
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

        try:
            with self.connection.conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO chunks (
                        document_id, chunk_number, chunk_text, embedding
                    ) VALUES (
                        %s, %s, %s, %s
                    )
                    """,
                    (
                        self.document_id,
                        self.chunk_number,
                        self.chunk_text,
                        self.embedding,
                    ),
                )

            self.connection.conn.commit()
        except errors.IntegrityError as ex:
            print(f"Duplicate id exception: {ex}")
            self.connection.conn.rollback()
        except errors.ForeignKeyViolation as ex:
            print(f"Document id not found exception: {ex}")
            self.connection.conn.rollback()
        except errors.OperationalError as ex:
            print(f"Insert error: {ex}")
            raise

    def search(self, chunk_text: str):
        try:
            with self.connection.conn.cursor() as cur:
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
