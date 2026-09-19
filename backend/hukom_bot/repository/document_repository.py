from psycopg import errors
from uuid import UUID
from psycopg import AsyncConnection
from backend.hukom_bot.enum.upload_status import UploadStatus
from backend.hukom_bot.database.database import Database
from backend.hukom_bot.model.document_model import Document
from backend.hukom_bot.schema.admin_schema import MonthlyCount
from backend.hukom_bot.schema.document_schema import *
from backend.hukom_bot.schema.admin_schema import (
    DocumentStatusCount,
    DocumentWeeklyCount,
    DocumentTypeCount,
)
from backend.hukom_bot.util.document_caster import DocumentCaster
from backend.hukom_bot.util.utility import build_date_range_where_clause


class DocumentRepository:
    def __init__(self, db: Database):
        self._database = db

    # CREATE ============================================================================

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

    # UPDATE ============================================================================

    async def update(
        self,
        document: DocumentUpdate,
        connection: AsyncConnection = None,
    ):
        if not document.model_dump(exclude={"id"}, exclude_none=True):
            return

        if connection is not None:
            await self._update_implement(connection, document)
            return

        async with self._database.connection() as conn:
            try:
                await self._update_implement(conn, document)
                await conn.commit()
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
        if document.rejection_message:
            set_clauses.append("rejection_message = %(rejection_message)s")
            values["rejection_message"] = document.rejection_message

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

    # READ ==============================================================================

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

    async def search(
        self, param: DocumentSearch, connection: AsyncConnection = None
    ) -> list[Document]:
        if connection is not None:
            return await self._search_implement(conn=connection, param=param)

        async with self._database.connection() as conn:
            try:
                result = await self._search_implement(conn=conn, param=param)
                await conn.commit()
                return result
            except errors.OperationalError as ex:
                await conn.rollback()
                raise

    async def _search_implement(self, conn: AsyncConnection, param: DocumentSearch):
        uploader_id_query = (
            "AND d.uploader_id = %(uploader_id)s"
            if param.uploader_id is not None
            else ""
        )

        upload_status_query = (
            "AND d.upload_status = %(upload_status)s"
            if param.upload_status is not None
            else ""
        )
        column_order = ", ".join(f"{col} {param.order.value}" for col in param.column)

        async with conn.cursor() as cur:
            await cur.execute(
                f"""
                SELECT * FROM (
                    WITH query AS (
                        SELECT plainto_tsquery('english',  %(query)s) AS q
                    )
                    SELECT 
                        d.*,
                        ts_rank(d.search_vector, q.q) AS rank
                    FROM documents d, query q
                    WHERE d.search_vector @@ q.q
                    {uploader_id_query} {upload_status_query}
                    ORDER BY rank DESC                    
                ) ORDER BY {column_order}
                LIMIT %(limit)s
                OFFSET %(offset)s
                """,
                param.model_dump(),
            )

            rows = await cur.fetchall()

        documents = []
        for row in rows:
            documents.append(Document.model_validate(row))

            return documents

    async def all(
        self, param: DocumentGetAll, connection: AsyncConnection = None
    ) -> list[Document]:
        if connection is not None:
            return await self._all_implement(connection, param)

        async with self._database.connection() as conn:
            try:
                result = await self._all_implement(conn, param)
                await conn.commit()
                return result
            except errors.OperationalError as ex:
                await conn.rollback()
                raise

    async def _all_implement(
        self, conn: AsyncConnection, param: DocumentGetAll
    ) -> list[DocumentGetAll]:
        column_order = ", ".join(f"{col} {param.order.value}" for col in param.column)

        async with conn.cursor() as cur:
            conditions = []
            if param.uploader_id is not None:
                conditions.append("uploader_id = %(uploader_id)s")
            if param.upload_status is not None:
                conditions.append("upload_status = %(upload_status)s")

            where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

            await cur.execute(
                f"""
                SELECT * 
                FROM documents
                {where_clause}
                ORDER BY {column_order}
                LIMIT %(limit)s
                OFFSET %(offset)s
                """,
                param.model_dump(),
            )

            rows = await cur.fetchall()

        documents = []
        for row in rows:
            documents.append(Document.model_validate(row))

        return documents

    async def count_all(
        self, date_range: DateRangeableMixin = None, connection: AsyncConnection = None
    ):
        if connection is not None:
            return await self._count_all_implement(
                conn=connection, date_range=date_range
            )

        try:
            async with self._database.connection() as conn:
                return await self._count_all_implement(conn=conn, date_range=date_range)
        except errors.OperationalError:
            raise

    async def _count_all_implement(
        self, conn: AsyncConnection, date_range: DateRangeableMixin = None
    ) -> int:
        async with conn.cursor() as cur:
            date_range_query = (
                build_date_range_where_clause(
                    column_name="created_at",
                    date_rangeable=date_range,
                    include_where=True,
                )
                if date_range
                else ""
            )

            await cur.execute(f"""SELECT COUNT(id) FROM documents {date_range_query}""")

            row = await cur.fetchone()
            return row["count"]

    async def count_by_upload_status(
        self, date_range: DateRangeableMixin = None, connection: AsyncConnection = None
    ):
        if connection is not None:
            return await self._count_by_upload_status_implement(
                conn=connection, date_range=date_range
            )

        try:
            async with self._database.connection() as conn:
                return await self._count_by_upload_status_implement(
                    conn=conn, date_range=date_range
                )
        except errors.OperationalError:
            raise

    async def _count_by_upload_status_implement(
        self, conn: AsyncConnection, date_range: DateRangeableMixin | None
    ):
        async with conn.cursor() as cur:
            date_range_query = (
                build_date_range_where_clause(
                    column_name="created_at",
                    date_rangeable=date_range,
                    include_where=True,
                )
                if date_range is not None
                else ""
            )

            await cur.execute(f"""
                SELECT 
                    upload_status AS status, 
                    COUNT(*) AS total_count
                FROM documents
                {date_range_query}
                GROUP BY upload_status
                ORDER BY total_count DESC;
                """)

            rows = await cur.fetchall()
            if not rows:
                return DocumentStatusCount()

            status_count = {row["status"]: row["total_count"] for row in rows}

            return DocumentStatusCount(**status_count)

    async def count_weekly(self, connection: AsyncConnection = None):
        if connection is not None:
            return await self._count_weekly_implement(conn=connection)

        try:
            async with self._database.connection() as conn:
                return await self._count_weekly_implement(conn=conn)
        except errors.OperationalError:
            raise

    async def _count_weekly_implement(self, conn: AsyncConnection):
        async with conn.cursor() as cur:
            await cur.execute("""
                SELECT 
                    to_char(created_at, 'FMDay') AS day_name,
                    COUNT(*) AS total_count
                FROM documents
                WHERE created_at >= date_trunc('week', current_date)
                AND created_at <  date_trunc('week', current_date) + INTERVAL '7 days'
                GROUP BY to_char(created_at, 'FMDay'), created_at::date, EXTRACT(isodow FROM created_at)
                ORDER BY EXTRACT(isodow FROM created_at) ASC
                """)

            rows = await cur.fetchall()
            if not rows:
                return DocumentWeeklyCount()

            daily_counts = {row["day_name"]: row["total_count"] for row in rows}

            return DocumentWeeklyCount(**daily_counts)

    async def count_monthly_upload(
        self, year: int = datetime.now().year, connection: AsyncConnection = None
    ):
        if connection is not None:
            return await self._count_monthly_upload_implement(
                conn=connection, year=year
            )

        try:
            async with self._database.connection() as conn:
                return await self._count_monthly_upload_implement(
                    conn=conn, year=year
                )
        except errors.OperationalError:
            raise

    async def _count_monthly_upload_implement(
        self, conn: AsyncConnection, year: int
    ):
        async with conn.cursor() as cur:
            await cur.execute(
                f"""
                SELECT 
                    lower(left(to_char(created_at, 'FMMonth'), 1)) || 
                        substring(to_char(created_at, 'FMMonth') from 2) AS month_name,
                    COUNT(*) AS total_count
                FROM documents
                WHERE EXTRACT(YEAR FROM created_at) = %s
                GROUP BY 
                    date_trunc('month', created_at), 
                    to_char(created_at, 'FMMonth')
                ORDER BY 
                    date_trunc('month', created_at) ASC;
                """,
                (year,),
            )

            rows = await cur.fetchall()
            if not rows:
                return MonthlyCount()

            monthly_counts = {row["month_name"]: row["total_count"] for row in rows}

            return MonthlyCount(**monthly_counts)

    async def count_registration(
            self, interval_days: int = 360, connection: AsyncConnection = None
        ):
            if connection is not None:
                return await self._count_registration_implement(
                    conn=connection, interval_days=interval_days
                )
    
            try:
                async with self._database.connection() as conn:
                    return await self._count_registration_implement(
                        conn=conn, interval_days=interval_days
                    )
            except errors.OperationalError:
                raise
    
    async def _count_registration_implement(
        self, conn: AsyncConnection, interval_days: int
    ):
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT COUNT(*) FROM documents
                WHERE created_at >= CURRENT_DATE - INTERVAL '%s days';
                """,
                (interval_days,),
            )

            row = await cur.fetchone()
            return row["count"]

    async def count_by_document_type(
        self,
        date_range: DateRangeableMixin = None,
        connection: AsyncConnection = None,
    ):
        if connection is not None:
            return await self._count_by_document_type_implement(
                conn=connection, date_range=date_range
            )

        try:
            async with self._database.connection() as conn:
                return await self._count_by_document_type_implement(
                    conn=conn, date_range=date_range
                )
        except errors.OperationalError:
            raise

    async def _count_by_document_type_implement(
        self, conn: AsyncConnection, date_range: DateRangeableMixin | None
    ):
        async with conn.cursor() as cur:
            date_range_query = (
                build_date_range_where_clause(
                    column_name="created_at",
                    date_rangeable=date_range,
                    include_where=True,
                )
                if date_range is not None
                else ""
            )

            await cur.execute(f"""
                SELECT 
                    document_type AS type,
                    COUNT(*) AS total_count
                FROM documents
                {date_range_query}
                GROUP BY document_type
                ORDER BY total_count DESC;
                """)

            rows = await cur.fetchall()
            if not rows:
                return DocumentTypeCount()

            type_counts = {row["type"]: row["total_count"] for row in rows}

            return DocumentTypeCount(**type_counts)

    # DELETE ============================================================================

    async def delete_many(self, ids: list[UUID], connection: AsyncConnection = None):
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

    async def _delete_many_implement(self, conn: AsyncConnection, ids: list[UUID]):
        async with conn.cursor() as cur:
            placeholders = ", ".join(["%s"] * len(ids))
            await cur.execute(
                f"""
                DELETE FROM documents
                WHERE id IN ({placeholders})
                """,
                ids,
            )
