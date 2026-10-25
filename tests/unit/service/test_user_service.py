import pytest
import pytest_asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

from backend.hukom_bot.service.user_service import UserService
from backend.hukom_bot.schema.user_schema import UserCreate, UserUpdate, UserSearch, UserGetByManyId, UserGetAll
from backend.hukom_bot.exception.file_exception import InvalidFileTypeException


class TestUserService:
    """Tests for UserService methods."""

    @pytest.fixture
    def mock_user_repo(self):
        """Mock UserRepository."""
        repo = MagicMock()
        repo.create = AsyncMock(return_value={"id": uuid4()})
        repo.update = AsyncMock()
        repo.get_by_id = AsyncMock(return_value=None)
        repo.get_by_many_id = AsyncMock(return_value=[])
        repo.get_by_provider_id = AsyncMock(return_value=None)
        repo.get_most_upload_count = AsyncMock(return_value=[])
        repo.search = AsyncMock(return_value=[])
        repo.all = AsyncMock(return_value=[])
        repo.count_all = AsyncMock(return_value=100)
        repo.count_active = AsyncMock(return_value=80)
        repo.count_inactive = AsyncMock(return_value=20)
        repo.count_monthly_registration = AsyncMock(return_value=[{"month": "2024-01", "count": 10}])
        repo.count_registration = AsyncMock(return_value=5)
        repo.count_by_role = AsyncMock(return_value={"admin": 1, "standard": 80, "contributor": 19})
        repo.delete = AsyncMock()
        return repo

    @pytest.fixture
    def mock_db(self):
        """Mock Database."""
        return MagicMock()

    @pytest.fixture
    def user_service(self, mock_db, mock_user_repo):
        """Create UserService instance with mocked dependencies."""
        return UserService(db=mock_db, user_repo=mock_user_repo)

    # =========================================================================
    # Repository Delegation Tests
    # =========================================================================

    @pytest.mark.asyncio
    async def test_create_delegates_to_repo(self, user_service, mock_user_repo):
        """create() should delegate to user_repo.create()."""
        user_data = UserCreate(
            id=uuid4(),
            provider_id="test_provider",
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            role="standard",
            provider="google",
        )
        connection = MagicMock()

        result = await user_service.create(user_data, connection=connection)

        mock_user_repo.create.assert_called_once_with(user=user_data, connection=connection)

    @pytest.mark.asyncio
    async def test_update_delegates_to_repo(self, user_service, mock_user_repo):
        """update() should delegate to user_repo.update()."""
        update_data = UserUpdate(
            id=uuid4(),
            first_name="Jane",
            last_name="Smith",
        )
        connection = MagicMock()

        await user_service.update(update_data, connection=connection)

        mock_user_repo.update.assert_called_once_with(user=update_data, connection=connection)

    @pytest.mark.asyncio
    async def test_get_by_id_delegates_to_repo(self, user_service, mock_user_repo):
        """get_by_id() should delegate to user_repo.get_by_id()."""
        user_id = str(uuid4())
        connection = MagicMock()

        await user_service.get_by_id(user_id, connection=connection)

        mock_user_repo.get_by_id.assert_called_once_with(id=user_id, connection=connection)

    @pytest.mark.asyncio
    async def test_get_by_ids_delegates_to_repo(self, user_service, mock_user_repo):
        """get_by_ids() should delegate to user_repo.get_by_many_id()."""
        param = UserGetByManyId(ids=[uuid4(), uuid4()])
        connection = MagicMock()

        await user_service.get_by_ids(param, connection=connection)

        mock_user_repo.get_by_many_id.assert_called_once_with(param=param, connection=connection)

    @pytest.mark.asyncio
    async def test_get_by_provider_id_delegates_to_repo(self, user_service, mock_user_repo):
        """get_by_provider_id() should delegate to user_repo.get_by_provider_id()."""
        provider_id = "test_provider"
        connection = MagicMock()

        await user_service.get_by_provider_id(provider_id, connection=connection)

        mock_user_repo.get_by_provider_id.assert_called_once_with(provider_id=provider_id, connection=connection)

    @pytest.mark.asyncio
    async def test_get_most_upload_count_delegates_to_repo(self, user_service, mock_user_repo):
        """get_most_upload_count() should delegate to user_repo.get_most_upload_count()."""
        connection = MagicMock()

        await user_service.get_most_upload_count(limit=5, connection=connection)

        mock_user_repo.get_most_upload_count.assert_called_once_with(limit=5, connection=connection)

    @pytest.mark.asyncio
    async def test_search_delegates_to_repo(self, user_service, mock_user_repo):
        """search() should delegate to user_repo.search()."""
        search_param = UserSearch(query="john", limit=10)
        connection = MagicMock()

        await user_service.search(search_param, connection=connection)

        mock_user_repo.search.assert_called_once_with(user=search_param, connection=connection)

    @pytest.mark.asyncio
    async def test_all_delegates_to_repo(self, user_service, mock_user_repo):
        """all() should delegate to user_repo.all()."""
        param = UserGetAll(limit=10)
        connection = MagicMock()

        await user_service.all(param, connection=connection)

        mock_user_repo.all.assert_called_once_with(param=param, connection=connection)

    @pytest.mark.asyncio
    async def test_count_all_delegates_to_repo(self, user_service, mock_user_repo):
        """count_all() should delegate to user_repo.count_all()."""
        connection = MagicMock()

        await user_service.count_all(connection=connection)

        mock_user_repo.count_all.assert_called_once_with(date_range=None, connection=connection)

    @pytest.mark.asyncio
    async def test_count_active_delegates_to_repo(self, user_service, mock_user_repo):
        """count_active() should delegate to user_repo.count_active()."""
        connection = MagicMock()

        await user_service.count_active(connection=connection)

        mock_user_repo.count_active.assert_called_once_with(date_range=None, connection=connection)

    @pytest.mark.asyncio
    async def test_count_inactive_delegates_to_repo(self, user_service, mock_user_repo):
        """count_inactive() should delegate to user_repo.count_inactive()."""
        connection = MagicMock()

        await user_service.count_inactive(connection=connection)

        mock_user_repo.count_inactive.assert_called_once_with(date_range=None, connection=connection)

    @pytest.mark.asyncio
    async def test_count_monthly_registration_delegates_to_repo(self, user_service, mock_user_repo):
        """count_monthly_registration() should delegate to user_repo.count_monthly_registration()."""
        connection = MagicMock()

        await user_service.count_monthly_registration(connection=connection)

        mock_user_repo.count_monthly_registration.assert_called_once_with(year=datetime.now().year, connection=connection)

    @pytest.mark.asyncio
    async def test_count_registration_delegates_to_repo(self, user_service, mock_user_repo):
        """count_registration() should delegate to user_repo.count_registration()."""
        connection = MagicMock()

        await user_service.count_registration(connection=connection)

        mock_user_repo.count_registration.assert_called_once_with(interval_days=360, connection=connection)

    @pytest.mark.asyncio
    async def test_count_by_role_delegates_to_repo(self, user_service, mock_user_repo):
        """count_by_role() should delegate to user_repo.count_by_role()."""
        connection = MagicMock()

        await user_service.count_by_role(connection=connection)

        mock_user_repo.count_by_role.assert_called_once_with(date_range=None, connection=connection)

    @pytest.mark.asyncio
    async def test_delete_delegates_to_repo(self, user_service, mock_user_repo):
        """delete() should delegate to user_repo.delete()."""
        user_id = uuid4()
        connection = MagicMock()

        await user_service.delete(user_id, connection=connection)

        mock_user_repo.delete.assert_called_once_with(id=user_id, connection=connection)

    # =========================================================================
    # Image Validation Tests
    # =========================================================================

    def test_is_valid_image_type_jpeg(self, user_service):
        """is_valid_image_type() should return True for JPEG images."""
        # JPEG magic bytes
        jpeg_content = b"\xff\xd8\xff\xe0\x00\x10JFIF"
        result = user_service.is_valid_image_type(jpeg_content)
        assert result is True

    def test_is_valid_image_type_png(self, user_service):
        """is_valid_image_type() should return True for PNG images."""
        # PNG magic bytes - need proper PNG header
        png_content = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
        result = user_service.is_valid_image_type(png_content)
        assert result is True

    def test_is_valid_image_type_jpg(self, user_service):
        """is_valid_image_type() should return True for JPG images."""
        jpg_content = b"\xff\xd8\xff\xe1"
        result = user_service.is_valid_image_type(jpg_content)
        assert result is True

    def test_is_valid_image_type_invalid(self, user_service):
        """is_valid_image_type() should return False for invalid types."""
        text_content = b"This is a text file"
        result = user_service.is_valid_image_type(text_content)
        assert result is False

    def test_is_valid_image_type_pdf(self, user_service):
        """is_valid_image_type() should return False for PDF (not an image)."""
        pdf_content = b"%PDF-1.4"
        result = user_service.is_valid_image_type(pdf_content)
        assert result is False