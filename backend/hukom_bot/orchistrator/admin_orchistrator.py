from backend.hukom_bot.database.database import Database
from backend.hukom_bot.service.chunk_service import ChunkService
from backend.hukom_bot.service.document_service import DocumentService
from backend.hukom_bot.service.user_service import UserService
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

    async def get_dashboard_data(self) -> AdminDashboardData:
        to_return = AdminDashboardData()
        async with self._db.connection() as conn:
            # User
            to_return.active_user_count = await self._user_service.count_active(
                connection=conn
            )

            # Documents
            to_return.documents_count = await self._document_service.count_all(
                connection=conn
            )

            to_return.pending_document_count = (
                await self._document_service.count_pending(connection=conn)
            )

            to_return.ongoing_document_count = (
                await self._document_service.count_ongoing(connection=conn)
            )

            to_return.completed_document_count = (
                await self._document_service.count_completed(connection=conn)
            )

            to_return.failed_document_count = await self._document_service.count_failed(
                connection=conn
            )

            to_return.rejected_document_count = (
                await self._document_service.count_rejected(connection=conn)
            )

            # Chunks
            to_return.chunks_count = await self._chunk_service.count_all(
                connection=conn
            )

            await conn.commit()

            return to_return
