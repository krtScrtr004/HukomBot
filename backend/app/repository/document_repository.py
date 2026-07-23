from typing import List
from psycopg import errors
from uuid import UUID
from psycopg import AsyncConnection

from backend.app.enum.upload_status import UploadStatus
from backend.app.database.database import Database
from backend.app.model.document_model import Document
from backend.app.schema.document_schema import DocumentCreate, DocumentUpdate
from backend.app.util.document_caster import DocumentCaster


class DocumentRepository:
    def __init__(self, db: Database):
        self._database = db

    async def create(
        self,
        document: DocumentCreate,
        connection: AsyncConnection = None,
    ) -> Document:
        if connection is not None:
            return await self._create_implement(connection, document)

        async with self._database.connection() as conn:
            try:
                result = await self._create_implement(conn, document)
                await conn.commit()
                return result
            except (errors.IntegrityError, errors.OperationalError) as ex:
                await conn.rollback()
                raise

    async def _create_implement(
        self,
        conn: AsyncConnection,
        document: DocumentCreate,
    ) -> Document:
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
                    uploader_id,
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
                    %(uploader_id)s,
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

        return DocumentCaster.create_to_base(document)

    async def update(
        self,
        document: DocumentUpdate,
        connection: AsyncConnection = None,
    ):
        if not document.model_dump(exclude={"id"}, exclude_none=True):
            return

        if connection is not None:
            return await self._update_implement(connection, document)

        async with self._database.connection() as conn:
            try:
                result = await self._update_implement(conn, document)
                await conn.commit()
                return result
            except (errors.IntegrityError, errors.OperationalError) as ex:
                await conn.rollback()
                raise

    async def _update_implement(self, conn: AsyncConnection, document: DocumentUpdate):
        query, params = self._build_update_query(document)

        async with conn.cursor() as cur:
            await cur.execute(query, params)

    def _build_update_query(self, document: DocumentUpdate) -> tuple[str, tuple]:
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

    async def get_by_id(
        self, id: UUID, connection: AsyncConnection = None
    ) -> Document | None:
        if connection is not None:
            return await self._get_by_id_implement(connection, id)

        async with self._database.connection() as conn:
            try:
                result = await self._get_by_id_implement(conn, id)
                await conn.commit()
                return result
            except errors.OperationalError as ex:
                await conn.rollback()
                raise

    async def _get_by_id_implement(self, conn: AsyncConnection, id: UUID):
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
        return Document.model_validate(row) if row is not None else None

    async def get_by_digest(
        self, digest: bytes, connection: AsyncConnection = None
    ) -> Document | None:
        if connection is not None:
            return await self._get_by_digest_implement(connection, digest)

        async with self._database.connection() as conn:
            try:
                result = await self._get_by_digest_implement(conn, digest)
                await conn.commit()
                return result
            except errors.OperationalError as ex:
                await conn.rollback()
                raise

    async def _get_by_digest_implement(self, conn: AsyncConnection, digest: bytes):
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
        return Document.model_validate(row) if row is not None else None

    async def get_upload_status_by_id(
        self, document_id: UUID, connection: AsyncConnection = None
    ) -> UploadStatus | None:
        if connection is not None:
            return await self._get_upload_status_by_id_implement(
                connection, document_id
            )

        async with self._database.connection() as conn:
            try:
                result = await self._get_upload_status_by_id_implement(
                    conn, document_id
                )
                await conn.commit()
                return result
            except errors.OperationalError as ex:
                await conn.rollback()
                raise

    async def _get_upload_status_by_id_implement(
        self, conn: AsyncConnection, document_id: UUID
    ):
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
        return (
            UploadStatus(row["upload_status"])
            if row is not None and row["upload_status"] is not None
            else None
        )

    async def delete_many(self, ids: List[UUID], connection: AsyncConnection = None):
        if not ids:
            return

        if connection is not None:
            return await self._delete_many_implement(connection, ids)

        async with self._database.connection() as conn:
            try:
                result = await self._delete_many_implement(conn, ids)
                await conn.commit()
                return result
            except (errors.IntegrityError, errors.OperationalError) as ex:
                await conn.rollback()
                raise

    async def _delete_many_implement(self, conn: AsyncConnection, ids: List[UUID]):
        async with conn.cursor() as cur:
            placeholders = ", ".join(["%s"] * len(ids))
            await cur.execute(
                f"""
                DELETE FROM documents
                WHERE id IN ({placeholders})
                """,
                ids,
            )
