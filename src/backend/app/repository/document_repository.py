from backend.app.database.database import Database
from backend.app.model.document_model import Document
from backend.app.schema.document_schema import DocumentCreate, DocumentSearch
from typing import List
from psycopg import errors
from datetime import datetime
from uuid import UUID


class DocumentRepository:
    def __init__(self, db: Database):
        self.database = db

    async def create(self, document: DocumentCreate) -> Document:
        async with self.database.connection() as conn:
            try:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        INSERT INTO documents (title, file_type, created_at)
                        VALUES (%(title)s, %(file_type)s, %(created_at)s)
                        ON CONFLICT (title)
                        DO UPDATE SET file_type = EXCLUDED.file_type
                        RETURNING id
                        """,
                        (document.model_dump()),
                    )
                    document_id = await cur.fetchone()["id"]
                await conn.commit()
            except (errors.IntegrityError, errors.OperationalError) as ex:
                await conn.rollback()
                raise

        return Document(
            id=document_id,
            title=document.title,
            file_type=document.file_type,
            created_at=document.created_at,
        )

    async def create_many(self, documents: List[DocumentCreate]) -> List[Document]:
        # Return if list is empty
        if not documents:
            return

        async with self.database.connection() as conn:
            try:
                async with conn.cursor() as cur:
                    await cur.executemany(
                        """
                        INSERT INTO documents (title, file_type, created_at) 
                        VALUES (%(title)s, %(file_type)s, %(created_at)s) 
                        ON DUPLICATE SET
                            file_type = EXCULDED.file_type
                        RETURNING id
                        """,
                        [docu.model_dump() for docu in documents],
                        returning=True,
                    )

                    # Retrieve the generated IDs
                    updated = []
                    counter = 0
                    while True:
                        row = await cur.fetchone()
                        if row:
                            # Update the document's ID attribute
                            updated.extends(
                                Document(
                                    id=row["id"],
                                    title=documents[counter].title,
                                    file_type=documents[counter].file_type,
                                    created_at=documents[counter].created_at,
                                )
                            )
                            counter += 1
                        if not await cur.nextset():
                            break

                await conn.commit()
                return updated
            except (errors.IntegrityError, errors.OperationalError) as ex:
                await conn.rollback()
                raise

    async def search(self, document: DocumentSearch) -> List:
        async with self.database.connection() as conn:
            try:
                search_comps = [document.title, document.file_type]
                terms = " ".join([item for item in search_comps if item])

                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        WITH query AS (
                            SELECT plainto_tsquery('english', %s) AS q
                        )
                        SELECT
                            d.*,
                            ts_rank(d.search_vector, q.q) AS rank
                        FROM documents d, query q
                        WHERE d.search_vector @@ q.q
                        ORDER BY rank DESC
                        LIMIT %s
                        OFFSET %s
                        """,
                        (terms, document.limit, document.offset),
                    )

                    rows = await cur.fetchall()

                    documents = []
                    for row in rows:
                        documents.append(Document.model_validate(row))

                    return documents
            except errors.OperationalError as ex:
                raise

    async def delete(self, id: UUID):
        async with self.database.connection() as conn:
            try:
                async with conn.cursor() as cur:
                    await cur.execute(
                        f"""
                        DELETE FROM documents
                        WHERE id = %s) 
                        """,
                        id,
                    )

                await conn.commit()
            except (errors.IntegrityError, errors.OperationalError) as ex:
                await conn.rollback()
                raise

    async def delete_many(self, ids: List[UUID]):
        if not ids:
            return

        async with self.database.connection() as conn:
            try:
                async with conn.cursor() as cur:
                    placeholders = ", ".join(["%s"] * len(ids))
                    await cur.execute(
                        f"""
                        DELETE FROM documents
                        WHERE id IN ({placeholders})
                        """,
                        ids,
                    )

                await conn.commit()
            except (errors.IntegrityError, errors.OperationalError) as ex:
                await conn.rollback()
                raise
