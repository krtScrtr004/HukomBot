from psycopg import AsyncConnection
from backend.hukom_bot.database.database import Database
from backend.hukom_bot.service.chunk_service import ChunkService
from backend.hukom_bot.service.document_service import DocumentService
from backend.hukom_bot.service.user_service import UserService
from backend.hukom_bot.schema.admin_schema import (
    AdminDashboardData,
    DocumentStatusCount,
    DocumentWeeklyCount,
)
from backend.hukom_bot.schema.mixin import DateRangeableMixin


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
