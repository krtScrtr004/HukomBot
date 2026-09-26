import asyncio
from psycopg import AsyncConnection
from backend.hukom_bot.database.database import Database
from backend.hukom_bot.service.chunk_service import ChunkService
from backend.hukom_bot.service.document_service import DocumentService
from backend.hukom_bot.service.user_service import UserService
from backend.hukom_bot.schema.admin_schema import (
    AdminDashboardData,
    AdminUserAnalytics,
    AdminDocumentAnalytics,
)
from backend.hukom_bot.schema.mixin import DateRangeableMixin
from backend.hukom_bot.util.user_caster import UserCaster


class AdminOrchistrator:
    def __init__(
        self,
        db: Database,
        chunk_service: ChunkService,
        document_service: DocumentService,
        user_service: UserService,
    ):
        self._db = db
        self._chunk_service = chunk_service
        self._document_service = document_service
        self._user_service = user_service

    async def get_dashboard_data(
        self, date_range: DateRangeableMixin
    ) -> AdminDashboardData:
        result = AdminDashboardData()

        async with self._db.connection() as conn:
            try:
                # User ========================================================
                result.active_user_count = await self._user_service.count_active(
                    date_range=date_range, connection=conn
                )

                # Documents ===================================================

                # All
                result.documents_count = await self._document_service.count_all(
                    date_range=date_range, connection=conn
                )

                # By Status
                result.document_status_count = (
                    await self._document_service.count_by_upload_status(
                        date_range=date_range, connection=conn
                    )
                )

                # By Document Type
                result.document_type_count = (
                    await self._document_service.count_by_document_type(
                        date_range=date_range, connection=conn
                    )
                )

                # Weekly (Mon to Sun)
                result.document_weekly_count = await self._document_service.count_weekly(
                    connection=conn
                )

                # Chunks =====================================================
                result.chunks_count = await self._chunk_service.count_all(
                    date_range=date_range, connection=conn
                )

                return result
            except asyncio.CancelledError:
                await self._handle_cancelled_error(conn=conn)

    async def get_user_analytics(self) -> AdminUserAnalytics:
        result = AdminUserAnalytics()

        async with self._db.connection() as conn:
            try:
                result.registered_count = await self._user_service.count_all(
                    connection=conn
                )

                result.active_count = await self._user_service.count_active(
                    connection=conn
                )

                result.inactive_count = await self._user_service.count_inactive(
                    connection=conn
                )

                result.monthly_registration_count = (
                    await self._user_service.count_monthly_registration(connection=conn)
                )

                # Last 30 days only
                result.new_registration_count = (
                    await self._user_service.count_registration(
                        interval_days=30, connection=conn
                    )
                )

                result.role_count = await self._user_service.count_by_role(
                    connection=conn
                )

                return result
            except asyncio.CancelledError:
                await self._handle_cancelled_error(conn=conn)

    async def get_document_analytics(self) -> AdminDocumentAnalytics:
        result = AdminDocumentAnalytics()

        async with self._db.connection() as conn:
            try:
                result.total_count = await self._document_service.count_all(
                    connection=conn
                )
                result.status_count = await self._document_service.count_by_upload_status(
                    connection=conn
                )
                result.type_count = await self._document_service.count_by_document_type(
                    connection=conn
                )
                result.monthly_upload_count = (
                    await self._document_service.count_monthly_upload(connection=conn)
                )
                result.new_upload_count = await self._document_service.count_registration(
                    interval_days=30,
                    connection=conn,
                )

                users = await self._user_service.get_most_upload_count(
                    limit=5,
                    connection=conn,
                )
                result.most_upload_user = [
                    UserCaster.base_to_response(user) for user in users
                ]

                return result

            except asyncio.CancelledError:
                await self._handle_cancelled_error(conn=conn)
    
    async def _handle_cancelled_error(self, conn: AsyncConnection):
        try:
            await asyncio.shield(conn.cancel_safe())
        except Exception:
            # The pool will discard the connection if it cannot recover it.
            pass
        raise