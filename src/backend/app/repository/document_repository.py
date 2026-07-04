from typing import List
from psycopg import errors
from uuid import UUID

from backend.app.database.database import Database
from backend.app.model.document_model import Document
from backend.app.schema.document_schema import DocumentCreate, DocumentUpdate, DocumentSearch


class DocumentRepository:
    def __init__(self, db: Database):
        self.database = db

    async def create(self, document: DocumentCreate) -> Document:
        async with self.database.connection() as conn:
            try:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        INSERT INTO documents (title, file_type, upload_status, upload_error, created_at)
                        VALUES (%(title)s, %(file_type)s, %(upload_status)s, %(upload_error)s, %(created_at)s)
                        ON CONFLICT (title)
                        DO UPDATE SET file_type = EXCLUDED.file_type
                        RETURNING id
                        """,
                        (document.model_dump()),
                    )
                    document_id = (await cur.fetchone())["id"]
                await conn.commit()
            except (errors.IntegrityError, errors.OperationalError) as ex:
                await conn.rollback()
                raise

        return Document(
            id=document_id,
            title=document.title,
            file_type=document.file_type,
            upload_status=document.upload_status,
            upload_error=document.upload_error,
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
                        INSERT INTO documents (title, file_type, upload_status, upload_error, created_at) 
                        VALUES (%(title)s, %(file_type)s, %(upload_status)s, %(upload_error)s, %(created_at)s) 
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
                            updated.append(
                                Document(
                                    id=row["id"],
                                    title=documents[counter].title,
                                    file_type=documents[counter].file_type,
                                    upload_status=documents[counter].upload_status,
                                    upload_error=documents[counter].upload_error,
                                    created_at=documents[counter].created_at,
                                )
                            )
                            counter += 1
                        if not cur.nextset():
                            break

                await conn.commit()
                return updated
            except (errors.IntegrityError, errors.OperationalError) as ex:
                await conn.rollback()
                raise

    async def update(self, document: DocumentUpdate): 
        if not document.model_dump(exclude={"id"}, exclude_none=True):
            return
        
        async with self.database.connection() as conn:
            query, params = self._build_update_query(document)            
            
            try:
                async with conn.cursor() as cur:
                    await cur.execute(query, params)
                await conn.commit()
            except (errors.IntegrityError, errors.OperationalError) as ex:
                await conn.rollback()
                raise   
            
    def _build_update_query(self, document: DocumentUpdate) -> tuple[str, tuple]:
        set_clauses = []
        values = {"id": document.id}

        if document.title:
            set_clauses.append("title = %(title)s")
            values["title"] = document.title
        if document.file_type:
            set_clauses.append("file_type = %(file_type)s")
            values["file_type"] = document.file_type
        if document.upload_status:
            set_clauses.append("upload_status = %(upload_status)s")
            values["upload_status"] = document.upload_status
        if document.upload_error:
            set_clauses.append("upload_error = %(upload_error)s")
            values["upload_error"] = document.upload_error

        if not set_clauses:
            raise RuntimeError("No fields to update")

        query = f"""
            UPDATE documents 
            SET {", ".join(set_clauses)}
            WHERE id = %(id)s
        """

        return query, values

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
