from backend.hukom_bot.database.database import Database
from backend.hukom_bot.service.chunk_service import ChunkService
from backend.hukom_bot.service.document_service import DocumentService
from backend.hukom_bot.service.user_service import UserService
from backend.hukom_bot.schema.mixin import DateRangeableMixin
from backend.hukom_bot.schema.util_schema import AdminDashboardData


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
            # User
            to_return.active_user_count = await self._user_service.count_active(
                date_range=date_range, connection=conn
            )

            # Documents
            to_return.documents_count = await self._document_service.count_all(
                date_range=date_range, connection=conn
            )

            to_return.pending_document_count = (
                await self._document_service.count_pending(
                    date_range=date_range, connection=conn
                )
            )

            to_return.ongoing_document_count = (
                await self._document_service.count_ongoing(
                    date_range=date_range, connection=conn
                )
            )

            to_return.completed_document_count = (
                await self._document_service.count_completed(
                    date_range=date_range, connection=conn
                )
            )

            to_return.failed_document_count = await self._document_service.count_failed(
                date_range=date_range, connection=conn
            )

            to_return.rejected_document_count = (
                await self._document_service.count_rejected(
                    date_range=date_range, connection=conn
                )
            )

            # Chunks
            to_return.chunks_count = await self._chunk_service.count_all(
                date_range=date_range, connection=conn
            )

            await conn.commit()

            return to_return
