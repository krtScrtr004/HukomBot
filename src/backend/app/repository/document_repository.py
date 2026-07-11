from typing import List
from psycopg import errors
from uuid import UUID

from backend.app.enum.upload_status import UploadStatus
from backend.app.database.database import Database
from backend.app.model.document_model import Document
from backend.app.schema.document_schema import (
    DocumentCreate,
    DocumentUpdate,
    DocumentSearch,
)


class DocumentRepository:
    def __init__(self, db: Database):
        self.__database = db

    async def create(self, document: DocumentCreate) -> Document:
        async with self.__database.connection() as conn:
            try:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        INSERT INTO documents (
                            id,
                            original_file_name, 
                            upload_file_name, 
                            document_type, 
                            file_type, 
                            upload_status, 
                            upload_error, 
                            digest,
                            created_at
                        ) VALUES (
                            %(id)s,
                            %(original_file_name)s, 
                            %(upload_file_name)s, 
                            %(document_type)s, 
                            %(file_type)s, 
                            %(upload_status)s, 
                            %(upload_error)s, 
                            %(digest)s,
                            %(created_at)s
                        )
                        ON CONFLICT (digest)
                            DO UPDATE SET
                                original_file_name  = EXCLUDED.original_file_name,
                                upload_file_name    = EXCLUDED.upload_file_name,
                                document_type       = EXCLUDED.document_type,
                                file_type           = EXCLUDED.file_type,
                                upload_status       = EXCLUDED.upload_status,
                                upload_error        = EXCLUDED.upload_error
                        """,
                        (document.model_dump()),
                    )
                await conn.commit()
                return Document(
                    id=document.id,
                    original_file_name=document.original_file_name,
                    upload_file_name=document.upload_file_name,
                    document_type=document.document_type,
                    file_type=document.file_type,
                    upload_status=document.upload_status,
                    upload_error=document.upload_error,
                    digest=document.digest,
                    created_at=document.created_at,
                )
            except (errors.IntegrityError, errors.OperationalError) as ex:
                await conn.rollback()
                raise

    async def create_many(self, documents: List[DocumentCreate]) -> List[Document]:
        # Return if list is empty
        if not documents:
            return

        async with self.__database.connection() as conn:
            try:
                async with conn.cursor() as cur:
                    await cur.executemany(
                        """
                        INSERT INTO documents (
                            id,
                            original_file_name, 
                            upload_file_name, 
                            document_type, 
                            file_type, 
                            upload_status, 
                            upload_error, 
                            digest,
                            created_at
                        ) VALUES (
                            %(id)s,
                            %(original_file_name)s, 
                            %(upload_file_name)s, 
                            %(document_type)s, 
                            %(file_type)s, 
                            %(upload_status)s, 
                            %(upload_error)s, 
                            %(digest)s,
                            %(created_at)s
                        )
                        ON CONFLICT (digest)
                            DO UPDATE SET 
                                original_file_name  = EXCLUDED.original_file_name,
                                upload_file_name    = EXCLUDED.upload_file_name,
                                document_type       = EXCLUDED.document_type,
                                file_type           = EXCLUDED.file_type,
                                upload_status       = EXCLUDED.upload_status,
                                upload_error        = EXCLUDED.upload_error
                        """,
                        [docu.model_dump() for docu in documents],
                        returning=True,
                    )

                    # Retrieve the generated IDs
                    updated = []
                    for i, _ in enumerate(documents):
                        # Update the document's ID attribute
                        updated.append(
                            Document(
                                id=documents[i].id,
                                original_file_name=documents[i].original_file_name,
                                upload_file_name=documents[i].upload_file_name,
                                document_type=documents[i].document_type,
                                file_type=documents[i].file_type,
                                upload_status=documents[i].upload_status,
                                upload_error=documents[i].upload_error,
                                digest=documents[i].digest,
                                created_at=documents[i].created_at,
                            )
                        )

                await conn.commit()
                return updated
            except (errors.IntegrityError, errors.OperationalError) as ex:
                await conn.rollback()
                raise

    async def update(self, document: DocumentUpdate):
        if not document.model_dump(exclude={"id"}, exclude_none=True):
            return

        async with self.__database.connection() as conn:
            query, params = self.__build_update_query(document)

            try:
                async with conn.cursor() as cur:
                    await cur.execute(query, params)
                await conn.commit()
            except (errors.IntegrityError, errors.OperationalError) as ex:
                await conn.rollback()
                raise

    def __build_update_query(self, document: DocumentUpdate) -> tuple[str, tuple]:
        set_clauses = []
        values = {"id": document.id}

        if document.original_file_name:
            set_clauses.append("original_file_name = %(original_file_name)s")
            values["original_file_name"] = document.original_file_name
        if document.upload_file_name:
            set_clauses.append("upload_file_name = %(upload_file_name)s")
            values["upload_file_name"] = document.upload_file_name
        if document.document_type:
            set_clauses.append("document_type = %(document_type)s")
            values["document_type"] = document.document_type.value
        if document.file_type:
            set_clauses.append("file_type = %(file_type)s")
            values["file_type"] = document.file_type
        if document.upload_error:
            set_clauses.append("upload_error = %(upload_error)s")
            values["upload_error"] = document.upload_error
        if document.upload_status:
            set_clauses.append("upload_status = %(upload_status)s")
            values["upload_status"] = document.upload_status

            # Set upload_error to None if status is COMPLETED
            if document.upload_status == UploadStatus.COMPLETED:
                set_clauses.append("upload_error = %(upload_error)s")
                values["upload_error"] = None

        if not set_clauses:
            raise RuntimeError("No fields to update")

        query = f"""
            UPDATE documents 
            SET {", ".join(set_clauses)}
            WHERE id = %(id)s
        """

        return query, values

    async def get_by_id(self, id: UUID) -> Document | None:
        async with self.__database.connection() as conn:
            try:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        SELECT *
                        FROM documents
                        WHERE id = %s
                        LIMIT 1
                        """,
                        (id,),
                    )

                    row = await cur.fetchone()

                await conn.commit()
                return Document.model_validate(row) if row is not None else None
            except errors.OperationalError as ex:
                raise

    async def get_by_original_file_name(
        self, original_file_name: str
    ) -> Document | None:
        async with self.__database.connection() as conn:
            try:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        SELECT *
                        FROM documents
                        WHERE original_file_name = %s
                        LIMIT 1
                        """,
                        (original_file_name.strip(),),
                    )

                    row = await cur.fetchone()

                await conn.commit()
                return Document.model_validate(row) if row is not None else None
            except errors.OperationalError as ex:
                raise

    async def get_by_digest(self, digest: bytes) -> Document | None:
        async with self.__database.connection() as conn:
            try:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        SELECT *
                        FROM documents
                        WHERE digest = %s
                        LIMIT 1
                        """,
                        (digest,),
                    )

                    row = await cur.fetchone()

                await conn.commit()
                return Document.model_validate(row) if row is not None else None
            except errors.OperationalError as ex:
                raise

    async def get_upload_status_by_id(self, document_id: UUID) -> UploadStatus | None:
        async with self.__database.connection() as conn:
            try:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        SELECT upload_status
                        FROM documents
                        WHERE id = %s
                        LIMIT 1
                        """,
                        (document_id,),
                    )

                    row = await cur.fetchone()

                await conn.commit()
                return (
                    UploadStatus(row["upload_status"])
                    if row is not None and row["upload_status"] is not None
                    else None
                )
            except errors.OperationalError as ex:
                raise

    async def search(self, document: DocumentSearch) -> List:
        async with self.__database.connection() as conn:
            try:
                search_comps = [
                    document.original_file_name,
                    document.document_type.value,
                    document.file_type,
                ]
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
        async with self.__database.connection() as conn:
            try:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        DELETE FROM documents
                        WHERE id = %s
                        """,
                        (id,),
                    )

                await conn.commit()
            except (errors.IntegrityError, errors.OperationalError) as ex:
                await conn.rollback()
                raise

    async def delete_many(self, ids: List[UUID]):
        if not ids:
            return

        async with self.__database.connection() as conn:
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
