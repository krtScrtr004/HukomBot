import pytest
import pytest_asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4
from io import BytesIO

from backend.hukom_bot.orchistrator.user_orchistrator import UserOrchistrator
from backend.hukom_bot.model.user_model import User
from backend.hukom_bot.enum.user_role import UserRole
from backend.hukom_bot.enum.oauth_provider import OAuthProvider
from backend.hukom_bot.schema.user_schema import UserUpdateBase, UserUpdate
from backend.hukom_bot.exception.app_exception import UnauthorizedException, NotFoundException
from backend.hukom_bot.exception.file_exception import InvalidFileTypeException, FileSizeTooLargeException


class TestUserOrchestrator:
    """Tests for UserOrchistrator.update_pipeline and _create_update_schema methods."""

    @pytest.fixture
    def mock_user_service(self):
        """Mock UserService."""
        service = MagicMock()
        service.is_valid_image_type = MagicMock(return_value=True)
        service.get_by_id = AsyncMock()
        service.update = AsyncMock()
        service.ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"]
        return service

    @pytest.fixture
    def mock_pubsub_service(self):
        """Mock PubsubService."""
        service = MagicMock()
        service.publish = AsyncMock(return_value=1)
        return service

    @pytest.fixture
    def orchestrator(self, mock_db, mock_user_service, mock_pubsub_service):
        """Create UserOrchistrator instance with mocked dependencies."""
        return UserOrchistrator(db=mock_db, user_service=mock_user_service, pubsub_service=mock_pubsub_service), mock_db.conn

    @pytest.fixture
    def admin_user(self):
        """Create admin user."""
        return User(
            id=uuid4(),
            provider_id="admin_provider",
            first_name="Admin",
            last_name="User",
            email="admin@example.com",
            role=UserRole.ADMIN,
            provider=OAuthProvider.GOOGLE,
            is_active=True,
            profile_picture=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            upload_count=0,
        )

    @pytest.fixture
    def standard_user(self):
        """Create standard user."""
        return User(
            id=uuid4(),
            provider_id="standard_provider",
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            role=UserRole.STANDARD,
            provider=OAuthProvider.GOOGLE,
            is_active=True,
            profile_picture=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            upload_count=0,
        )

    @pytest.fixture
    def target_user(self):
        """Create target user to be updated."""
        return User(
            id=uuid4(),
            provider_id="target_provider",
            first_name="Target",
            last_name="User",
            email="target@example.com",
            role=UserRole.STANDARD,
            provider=OAuthProvider.GOOGLE,
            is_active=True,
            profile_picture=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            upload_count=0,
        )

    # =========================================================================
    # Authorization Tests
    # =========================================================================

    @pytest.mark.asyncio
    async def test_update_pipeline_non_admin_updating_other_user_raises_401(
        self, orchestrator, standard_user, target_user
    ):
        """Non-admin updating another user should raise UnauthorizedException."""
        orch, conn = orchestrator

        with pytest.raises(UnauthorizedException) as exc_info:
            await orch.update_pipeline(
                me=standard_user,
                user_id=target_user.id,
                user=UserUpdateBase(first_name="New Name"),
                profile_picture=None,
            )

        assert "not allowed to perform update on other's information" in str(exc_info.value.details)

    @pytest.mark.asyncio
    async def test_update_pipeline_non_admin_updating_role_raises_401(
        self, orchestrator, standard_user
    ):
        """Non-admin setting their own role should raise UnauthorizedException."""
        orch, conn = orchestrator

        with pytest.raises(UnauthorizedException) as exc_info:
            await orch.update_pipeline(
                me=standard_user,
                user_id=standard_user.id,  # Updating own record
                user=UserUpdateBase(role=UserRole.ADMIN),
                profile_picture=None,
            )

        assert "not allowed to update application role" in str(exc_info.value.details)

    @pytest.mark.asyncio
    async def test_update_pipeline_non_admin_updating_is_active_raises_401(
        self, orchestrator, standard_user
    ):
        """Non-admin setting their own is_active should raise UnauthorizedException."""
        orch, conn = orchestrator

        with pytest.raises(UnauthorizedException) as exc_info:
            await orch.update_pipeline(
                me=standard_user,
                user_id=standard_user.id,  # Updating own record
                user=UserUpdateBase(is_active=False),
                profile_picture=None,
            )

        assert "not allowed to reactivate/deactivate your own account" in str(exc_info.value.details)

    @pytest.mark.asyncio
    async def test_update_pipeline_non_admin_uploading_profile_picture_for_other_raises_401(
        self, orchestrator, standard_user, target_user
    ):
        """Non-admin uploading profile picture for another user should raise UnauthorizedException.
        
        The code checks if user is updating another user's info first, which triggers
        before the profile picture check. This is the correct security behavior.
        """
        orch, conn = orchestrator

        # Create a mock UploadFile
        mock_file = MagicMock()
        mock_file.read = AsyncMock(return_value=b"fake image data")

        with pytest.raises(UnauthorizedException) as exc_info:
            await orch.update_pipeline(
                me=standard_user,
                user_id=target_user.id,
                user=UserUpdateBase(),  # Empty update object
                profile_picture=mock_file,
            )

        # The first check (non-admin updating other user) triggers
        assert "not allowed to perform update on other's information" in str(exc_info.value.details)

    @pytest.mark.asyncio
    async def test_update_pipeline_non_admin_uploading_profile_picture_for_self_succeeds(
        self, orchestrator, standard_user, mock_user_service
    ):
        """Non-admin uploading profile picture for themselves should succeed (if valid)."""
        orch, conn = orchestrator
        mock_user_service.is_valid_image_type.return_value = True

        mock_file = MagicMock()
        mock_file.read = AsyncMock(return_value=b"fake image data")

        with patch("backend.hukom_bot.orchistrator.user_orchistrator.upload_to_cloudinary") as mock_upload:
            mock_upload.return_value = MagicMock(secure_url="https://cloudinary.com/image.jpg", public_id="test_id")

            await orch.update_pipeline(
                me=standard_user,
                user_id=standard_user.id,
                user=UserUpdateBase(),  # Empty update object
                profile_picture=mock_file,
            )

        mock_user_service.update.assert_called_once()

    # =========================================================================
    # User Lookup Tests
    # =========================================================================

    @pytest.mark.asyncio
    async def test_update_pipeline_admin_updating_nonexistent_user_raises_404(
        self, orchestrator, admin_user, mock_user_service
    ):
        """Admin updating non-existent user should raise NotFoundException."""
        orch, conn = orchestrator
        mock_user_service.get_by_id.return_value = None

        with pytest.raises(NotFoundException) as exc_info:
            await orch.update_pipeline(
                me=admin_user,
                user_id=uuid4(),
                user=UserUpdateBase(first_name="New Name"),
                profile_picture=None,
            )

        assert exc_info.value.code == "USER_NOT_FOUND"
        assert "User not found" in exc_info.value.message

    # =========================================================================
    # Image Validation Tests
    # =========================================================================

    @pytest.mark.asyncio
    async def test_update_pipeline_invalid_mime_type_raises_exception(
        self, orchestrator, standard_user, mock_user_service
    ):
        """Invalid MIME type should raise InvalidFileTypeException."""
        orch, conn = orchestrator
        mock_user_service.is_valid_image_type.return_value = False

        mock_file = MagicMock()
        mock_file.read = AsyncMock(return_value=b"invalid file data")

        with pytest.raises(InvalidFileTypeException) as exc_info:
            await orch.update_pipeline(
                me=standard_user,
                user_id=standard_user.id,
                user=UserUpdateBase(),
                profile_picture=mock_file,
            )

        assert exc_info.value.code == "INVALID_IMAGE_TYPE"

    @pytest.mark.asyncio
    async def test_update_pipeline_file_too_large_raises_exception(
        self, orchestrator, standard_user, mock_user_service
    ):
        """File > 5MB should raise FileSizeTooLargeException."""
        orch, conn = orchestrator
        mock_user_service.is_valid_image_type.return_value = True

        # Create 6MB file content
        large_content = b"x" * (6 * 1024 * 1024)
        mock_file = MagicMock()
        mock_file.read = AsyncMock(return_value=large_content)

        with pytest.raises(FileSizeTooLargeException) as exc_info:
            await orch.update_pipeline(
                me=standard_user,
                user_id=standard_user.id,
                user=UserUpdateBase(),
                profile_picture=mock_file,
            )

        assert "Max size is 5242880" in str(exc_info.value.details)

    # =========================================================================
    # Success Path Tests
    # =========================================================================

    @pytest.mark.asyncio
    async def test_update_pipeline_update_first_name_last_name_only(
        self, orchestrator, standard_user, mock_user_service
    ):
        """Update first_name and last_name only."""
        orch, conn = orchestrator

        await orch.update_pipeline(
            me=standard_user,
            user_id=standard_user.id,
            user=UserUpdateBase(first_name="Jane", last_name="Smith"),
            profile_picture=None,
        )

        mock_user_service.update.assert_called_once()
        update_arg = mock_user_service.update.call_args[1]["user"]
        assert update_arg.first_name == "Jane"
        assert update_arg.last_name == "Smith"
        assert update_arg.profile_picture is None
        assert update_arg.role is None
        assert update_arg.is_active is None

    @pytest.mark.asyncio
    async def test_update_pipeline_update_profile_picture(
        self, orchestrator, standard_user, mock_user_service
    ):
        """Update profile picture."""
        orch, conn = orchestrator
        mock_user_service.is_valid_image_type.return_value = True

        mock_file = MagicMock()
        mock_file.read = AsyncMock(return_value=b"fake image data")

        with patch("backend.hukom_bot.orchistrator.user_orchistrator.upload_to_cloudinary") as mock_upload:
            mock_upload.return_value = MagicMock(secure_url="https://cloudinary.com/image.jpg", public_id="test_id")

            await orch.update_pipeline(
                me=standard_user,
                user_id=standard_user.id,
                user=UserUpdateBase(),
                profile_picture=mock_file,
            )

        mock_user_service.update.assert_called_once()
        update_arg = mock_user_service.update.call_args[1]["user"]
        assert update_arg.profile_picture == "https://cloudinary.com/image.jpg"

    @pytest.mark.asyncio
    async def test_update_pipeline_admin_updates_role(
        self, orchestrator, admin_user, target_user, mock_user_service
    ):
        """Admin updating another user's role."""
        orch, conn = orchestrator
        mock_user_service.get_by_id.return_value = target_user

        await orch.update_pipeline(
            me=admin_user,
            user_id=target_user.id,
            user=UserUpdateBase(role=UserRole.CONTRIBUTOR),
            profile_picture=None,
        )

        mock_user_service.update.assert_called_once()
        update_arg = mock_user_service.update.call_args[1]["user"]
        assert update_arg.role == UserRole.CONTRIBUTOR

    @pytest.mark.asyncio
    async def test_update_pipeline_admin_updates_is_active(
        self, orchestrator, admin_user, target_user, mock_user_service
    ):
        """Admin updating another user's is_active status."""
        orch, conn = orchestrator
        mock_user_service.get_by_id.return_value = target_user

        await orch.update_pipeline(
            me=admin_user,
            user_id=target_user.id,
            user=UserUpdateBase(is_active=False),
            profile_picture=None,
        )

        mock_user_service.update.assert_called_once()
        update_arg = mock_user_service.update.call_args[1]["user"]
        assert update_arg.is_active is False

    

    # =========================================================================
    # Rollback Tests
    # =========================================================================

    @pytest.mark.asyncio
    async def test_update_pipeline_rollback_on_db_failure(
        self, orchestrator, standard_user, mock_user_service
    ):
        """Cloudinary upload succeeds but DB update fails -> transaction rolled back, image removed."""
        orch, conn = orchestrator
        mock_user_service.is_valid_image_type.return_value = True
        mock_user_service.update.side_effect = Exception("DB Error")

        mock_file = MagicMock()
        mock_file.read = AsyncMock(return_value=b"fake image data")

        with patch("backend.hukom_bot.orchistrator.user_orchistrator.upload_to_cloudinary") as mock_upload, \
             patch("backend.hukom_bot.orchistrator.user_orchistrator.remove_from_cloudinary") as mock_remove:
            mock_upload.return_value = MagicMock(secure_url="https://cloudinary.com/image.jpg", public_id="test_public_id")
            mock_remove.return_value = True

            with pytest.raises(Exception, match="DB Error"):
                await orch.update_pipeline(
                    me=standard_user,
                    user_id=standard_user.id,
                    user=UserUpdateBase(),
                    profile_picture=mock_file,
                )

            conn.rollback.assert_called_once()
            mock_remove.assert_called_once_with(public_id="test_public_id")

    # =========================================================================
    # _create_update_schema Tests
    # =========================================================================

    def test_create_update_schema_only_modified_fields_included(
        self, orchestrator, standard_user
    ):
        """Only modified fields should be included in update schema."""
        orch, _ = orchestrator

        update_schema = orch._create_update_schema(
            user_id=standard_user.id,
            user=UserUpdateBase(first_name="Jane", last_name="Smith"),
            profile_url=None,
            existing_user=standard_user,
        )

        assert update_schema is not None
        assert update_schema.first_name == "Jane"
        assert update_schema.last_name == "Smith"
        assert update_schema.profile_picture is None
        assert update_schema.role is None
        assert update_schema.is_active is None

    def test_create_update_schema_profile_picture_unchanged_returns_none(
        self, orchestrator, standard_user
    ):
        """If profile_picture is unchanged, it should not be included."""
        orch, _ = orchestrator

        update_schema = orch._create_update_schema(
            user_id=standard_user.id,
            user=None,
            profile_url=standard_user.profile_picture,  # Same as existing
            existing_user=standard_user,
        )

        # Should return None because no changes
        assert update_schema is None

    def test_create_update_schema_profile_picture_changed_included(
        self, orchestrator, standard_user
    ):
        """If profile_picture is changed, it should be included."""
        orch, _ = orchestrator

        update_schema = orch._create_update_schema(
            user_id=standard_user.id,
            user=None,
            profile_url="https://new-image.jpg",
            existing_user=standard_user,
        )

        assert update_schema is not None
        assert update_schema.profile_picture == "https://new-image.jpg"

    def test_create_update_schema_no_changes_returns_none(
        self, orchestrator, standard_user
    ):
        """No user data and no profile picture change should return None."""
        orch, _ = orchestrator

        update_schema = orch._create_update_schema(
            user_id=standard_user.id,
            user=None,
            profile_url=None,
            existing_user=standard_user,
        )

        assert update_schema is None