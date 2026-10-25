import pytest
import pytest_asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

from backend.hukom_bot.orchistrator.admin_orchistrator import AdminOrchistrator
from backend.hukom_bot.schema.admin_schema import AdminDashboardData, AdminUserAnalytics, AdminDocumentAnalytics
from backend.hukom_bot.schema.mixin import DateRangeableMixin
from backend.hukom_bot.model.user_model import User
from backend.hukom_bot.enum.user_role import UserRole
from backend.hukom_bot.enum.oauth_provider import OAuthProvider


class TestAdminOrchestrator:
    """Tests for AdminOrchistrator analytics methods."""

    @pytest.fixture
    def mock_chunk_service(self):
        """Mock ChunkService."""
        service = MagicMock()
        service.count_all = AsyncMock(return_value=1000)
        return service

    @pytest.fixture
    def mock_document_service(self):
        """Mock DocumentService."""
        service = MagicMock()
        service.count_all = AsyncMock(return_value=500)
        service.count_by_upload_status = AsyncMock(return_value={
            "pending": 10,
            "ongoing": 5,
            "completed": 450,
            "failed": 20,
            "rejected": 15,
        })
        service.count_by_document_type = AsyncMock(return_value={
            "statute": 200,
            "contract": 150,
            "case_law": 100,
            "other": 50,
        })
        service.count_weekly = AsyncMock(return_value=[
            {"week_start": "2024-01-01", "count": 10},
            {"week_start": "2024-01-08", "count": 15},
        ])
        service.count_monthly_upload = AsyncMock(return_value={
            "2024-01": 100,
            "2024-02": 120,
        })
        service.count_registration = AsyncMock(return_value=50)
        return service

    @pytest.fixture
    def mock_user_service(self):
        """Mock UserService."""
        service = MagicMock()
        service.count_active = AsyncMock(return_value=80)
        service.count_all = AsyncMock(return_value=100)
        service.count_inactive = AsyncMock(return_value=20)
        service.count_monthly_registration = AsyncMock(return_value=[
            {"month": "2024-01", "count": 10},
            {"month": "2024-02", "count": 12},
        ])
        service.count_registration = AsyncMock(return_value=5)
        service.count_by_role = AsyncMock(return_value={
            "admin": 1,
            "standard": 80,
            "contributor": 19,
        })
        service.get_most_upload_count = AsyncMock(return_value=[])
        return service

    @pytest.fixture
    def orchestrator(self, mock_db, mock_chunk_service, mock_document_service, mock_user_service):
        """Create AdminOrchistrator instance with mocked dependencies."""
        return AdminOrchistrator(
            db=mock_db,
            chunk_service=mock_chunk_service,
            document_service=mock_document_service,
            user_service=mock_user_service,
        ), mock_db.conn

    @pytest.fixture
    def date_range_mixin(self):
        """Create a DateRangeableMixin instance."""
        class TestDateRange(DateRangeableMixin):
            date_start: datetime = datetime(2024, 1, 1)
            date_end: datetime = datetime(2024, 12, 31)
        return TestDateRange()

    # =========================================================================
    # get_dashboard_data Tests
    # =========================================================================

    @pytest.mark.asyncio
    async def test_get_dashboard_data_all_counts_populated(
        self, orchestrator, date_range_mixin, mock_user_service,
        mock_document_service, mock_chunk_service
    ):
        """All dashboard counts should be populated."""
        orch, conn = orchestrator

        result = await orch.get_dashboard_data(date_range_mixin)

        assert isinstance(result, AdminDashboardData)
        assert result.active_user_count == 80
        assert result.documents_count == 500
        assert result.chunks_count == 1000
        assert result.document_status_count == {
            "pending": 10,
            "ongoing": 5,
            "completed": 450,
            "failed": 20,
            "rejected": 15,
        }
        assert result.document_type_count == {
            "statute": 200,
            "contract": 150,
            "case_law": 100,
            "other": 50,
        }
        assert len(result.document_weekly_count) == 2

    @pytest.mark.asyncio
    async def test_get_dashboard_data_date_range_filtering(
        self, orchestrator, date_range_mixin, mock_user_service,
        mock_document_service, mock_chunk_service
    ):
        """Date range filtering should be passed to service methods."""
        orch, conn = orchestrator

        await orch.get_dashboard_data(date_range_mixin)

        # Verify date_range passed to all counting methods
        mock_user_service.count_active.assert_called_once_with(
            date_range=date_range_mixin, connection=conn
        )
        mock_document_service.count_all.assert_called_once_with(
            date_range=date_range_mixin, connection=conn
        )
        mock_document_service.count_by_upload_status.assert_called_once_with(
            date_range=date_range_mixin, connection=conn
        )
        mock_document_service.count_by_document_type.assert_called_once_with(
            date_range=date_range_mixin, connection=conn
        )
        mock_chunk_service.count_all.assert_called_once_with(
            date_range=date_range_mixin, connection=conn
        )

    @pytest.mark.asyncio
    async def test_get_dashboard_data_cancelled_error_handling(
        self, orchestrator, date_range_mixin, mock_user_service
    ):
        """CancelledError should be caught and handled."""
        orch, conn = orchestrator
        mock_user_service.count_active.side_effect = KeyboardInterrupt()

        with pytest.raises(KeyboardInterrupt):
            await orch.get_dashboard_data(date_range_mixin)

    # =========================================================================
    # get_user_analytics Tests
    # =========================================================================

    @pytest.mark.asyncio
    async def test_get_user_analytics_all_counts_populated(
        self, orchestrator, mock_user_service
    ):
        """All user analytics counts should be populated."""
        orch, conn = orchestrator

        result = await orch.get_user_analytics()

        assert isinstance(result, AdminUserAnalytics)
        assert result.registered_count == 100
        assert result.active_count == 80
        assert result.inactive_count == 20
        assert len(result.monthly_registration_count) == 2
        assert result.new_registration_count == 5
        assert result.role_count == {
            "admin": 1,
            "standard": 80,
            "contributor": 19,
        }

    @pytest.mark.asyncio
    async def test_get_user_analytics_cancelled_error_handling(
        self, orchestrator, mock_user_service
    ):
        """CancelledError should be caught and handled."""
        orch, conn = orchestrator
        mock_user_service.count_all.side_effect = KeyboardInterrupt()

        with pytest.raises(KeyboardInterrupt):
            await orch.get_user_analytics()

    # =========================================================================
    # get_document_analytics Tests
    # =========================================================================

    @pytest.mark.asyncio
    async def test_get_document_analytics_all_counts_populated(
        self, orchestrator, mock_document_service, mock_user_service
    ):
        """All document analytics counts should be populated including most_upload_user."""
        orch, conn = orchestrator

        # Mock most_upload_user return
        top_user = User(
            id=uuid4(),
            provider_id="top_provider",
            first_name="Top",
            last_name="Uploader",
            email="top@example.com",
            role=UserRole.STANDARD,
            provider=OAuthProvider.GOOGLE,
            is_active=True,
            profile_picture=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            upload_count=50,
        )
        mock_user_service.get_most_upload_count.return_value = [top_user]

        result = await orch.get_document_analytics()

        assert isinstance(result, AdminDocumentAnalytics)
        assert result.total_count == 500
        assert result.status_count == {
            "pending": 10,
            "ongoing": 5,
            "completed": 450,
            "failed": 20,
            "rejected": 15,
        }
        assert result.type_count == {
            "statute": 200,
            "contract": 150,
            "case_law": 100,
            "other": 50,
        }
        assert result.monthly_upload_count == {
            "2024-01": 100,
            "2024-02": 120,
        }
        assert result.new_upload_count == 50
        assert len(result.most_upload_user) == 1
        assert result.most_upload_user[0].upload_count == 50

    @pytest.mark.asyncio
    async def test_get_document_analytics_most_upload_user_mapping(
        self, orchestrator, mock_user_service
    ):
        """Most upload users should be properly mapped using UserCaster."""
        orch, conn = orchestrator

        users = [
            User(
                id=uuid4(),
                provider_id=f"user_{i}",
                first_name=f"User{i}",
                last_name="Test",
                email=f"user{i}@example.com",
                role=UserRole.STANDARD,
                provider=OAuthProvider.GOOGLE,
                is_active=True,
                profile_picture=None,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                upload_count=30 - 10 * i,  # 30, 20, 10
            )
            for i in range(3)
        ]
        mock_user_service.get_most_upload_count.return_value = users

        result = await orch.get_document_analytics()

        assert len(result.most_upload_user) == 3
        assert result.most_upload_user[0].upload_count == 30
        assert result.most_upload_user[1].upload_count == 20
        assert result.most_upload_user[2].upload_count == 10

    @pytest.mark.asyncio
    async def test_get_document_analytics_cancelled_error_handling(
        self, orchestrator, mock_document_service
    ):
        """CancelledError should be caught and handled."""
        orch, conn = orchestrator
        mock_document_service.count_all.side_effect = KeyboardInterrupt()

        with pytest.raises(KeyboardInterrupt):
            await orch.get_document_analytics()