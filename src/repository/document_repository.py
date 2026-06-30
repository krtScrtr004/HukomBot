from database.database import Database
from model.document_model import Document, DocumentCreate, DocumentSearch
from typing import List
from psycopg import errors
from datetime import datetime
from uuid import UUID


class DocumentRepository:
    def __init__(self):
        self.database = Database()

    def create(self, document: DocumentCreate) -> Document:
        with self.database.connection() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO documents (title, file_type, created_at)
                        VALUES (%(title)s, %(file_type)s, %(created_at)s)
                        ON CONFLICT (title)
                        DO UPDATE SET file_type = EXCLUDED.file_type
                        RETURNING id
                        """,
                        (document.model_dump()),
                    )
                    document_id = cur.fetchone()["id"]
                conn.commit()
            except (errors.IntegrityError, errors.OperationalError) as ex:
                print(f"DB error: {ex}")
                conn.rollback()
                raise

        return Document(
            id=document_id,
            title=document.title,
            file_type=document.file_type,
            created_at=document.created_at,
        )

    def create_many(self, documents: List[DocumentCreate]) -> List[Document]:
        # Return if list is empty
        if not documents:
            return

        with self.database.connection() as conn:
            try:
                with conn.cursor() as cur:
                    cur.executemany(
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
                        row = cur.fetchone()
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
                        if not cur.nextset():
                            break

                conn.commit()
                return updated
            except (errors.IntegrityError, errors.OperationalError) as ex:
                print(f"DB Error: {ex}")
                conn.rollback()
                raise

    def search(self, document: DocumentSearch) -> List:
        with self.database.connection() as conn:
            try:
                search_comps = [document.title, document.file_type]
                terms = " ".join([item for item in search_comps if item])

                with conn.cursor() as cur:
                    cur.execute(
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

                    rows = cur.fetchall()

                    documents = []
                    for row in rows:
                        documents.append(Document.model_validate(row))

                    return documents
            except errors.OperationalError as ex:
                print(f"DB error: {ex}")
                raise

    def delete_many(self, ids: List[UUID]):
        if not ids:
            return

        with self.database.connection() as conn:
            try:
                with conn.cursor() as cur:
                    placeholders = ", ".join(["%s"] * len(ids))
                    with conn.cursor() as cur:
                        cur.execute(
                            f"""
                            DELETE FROM documents
                            WHERE id IN ({placeholders})
                            """,
                            ids,
                        )

                conn.commit()
            except (errors.IntegrityError, errors.OperationalError) as ex:
                print(f"DB error: {ex}")
                conn.rollback()
                raise
