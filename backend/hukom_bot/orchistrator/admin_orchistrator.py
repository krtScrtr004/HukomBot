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
        to_return = AdminDashboardData()

        async with self._db.connection() as conn:
            # User ========================================================
            to_return.active_user_count = await self._user_service.count_active(
                date_range=date_range, connection=conn
            )

            # Documents ===================================================

            # All
            to_return.documents_count = await self._document_service.count_all(
                date_range=date_range, connection=conn
            )

            # By Status
            to_return.document_status_count = (
                await self._document_service.count_by_upload_status(
                    date_range=date_range, connection=conn
                )
            )

            # By Document Type
            to_return.document_type_count = (
                await self._document_service.count_by_document_type(
                    date_range=date_range, connection=conn
                )
            )

            # Weekly (Mon to Sun)
            to_return.document_weekly_count = await self._document_service.count_weekly(
                connection=conn
            )

            # Chunks =====================================================
            to_return.chunks_count = await self._chunk_service.count_all(
                date_range=date_range, connection=conn
            )

            await conn.commit()

            return to_return

    async def get_user_analytics(self) -> AdminUserAnalytics:
        to_return = AdminUserAnalytics()

        async with self._db.connection() as conn:
            to_return.registered_count = await self._user_service.count_all(
                connection=conn
            )

            to_return.active_count = await self._user_service.count_active(
                connection=conn
            )

            to_return.inactive_count = await self._user_service.count_inactive(
                connection=conn
            )

            to_return.monthly_registration_count = (
                await self._user_service.count_monthly_registration(connection=conn)
            )

            # Last 30 days only
            to_return.new_registration_count = (
                await self._user_service.count_registration(
                    interval_days=30, connection=conn
                )
            )

            to_return.role_count = await self._user_service.count_by_role(
                connection=conn
            )

            await conn.commit()

            return to_return

    async def get_document_analytics(self) -> AdminDocumentAnalytics:
        to_return = AdminDocumentAnalytics()

        async with self._db.connection() as conn:
            to_return.total_count = await self._document_service.count_all(
                connection=conn
            )

            to_return.status_count = (
                await self._document_service.count_by_upload_status(connection=conn)
            )

            to_return.type_count = await self._document_service.count_by_document_type(
                connection=conn
            )

            to_return.monthly_upload_count = (
                await self._document_service.count_monthly_upload(connection=conn)
            )

            to_return.new_upload_count = await self._document_service.count_registration(
                interval_days=30, connection=conn
            )

            most_upload_users = await self._user_service.get_most_upload_count(
                limit=15, connection=conn
            )
            to_return.most_upload_user = [
                UserCaster.base_to_response(user) for user in most_upload_users
            ]

            return to_return
