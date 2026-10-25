import pytest
import pytest_asyncio
from httpx import AsyncClient


class TestSetup:
    """Test that the test infrastructure works correctly."""
    
    def test_jwt_service_fixture(self, jwt_service):
        """Test that JWT service fixture works."""
        assert jwt_service is not None
        assert hasattr(jwt_service, 'encode')
        assert hasattr(jwt_service, 'verify')
    
    def test_admin_token_fixture(self, admin_token):
        """Test that admin token fixture generates a valid token."""
        assert admin_token is not None
        assert isinstance(admin_token, str)
        assert len(admin_token) > 0
        # JWT has 3 parts separated by dots
        assert admin_token.count('.') == 2
    
    def test_standard_token_fixture(self, standard_token):
        """Test that standard user token fixture works."""
        assert standard_token is not None
        assert isinstance(standard_token, str)
        assert standard_token.count('.') == 2
    
    def test_contributor_token_fixture(self, contributor_token):
        """Test that contributor token fixture works."""
        assert contributor_token is not None
        assert isinstance(contributor_token, str)
        assert contributor_token.count('.') == 2
    
    def test_expired_token_fixture(self, expired_token):
        """Test that expired token fixture works."""
        assert expired_token is not None
        assert isinstance(expired_token, str)
        assert expired_token.count('.') == 2
    
    def test_mock_db_fixture(self, mock_db):
        """Test that mock database fixture works."""
        assert mock_db is not None
        assert hasattr(mock_db, 'connection')
        assert hasattr(mock_db, 'cursor')
        assert hasattr(mock_db, 'conn')
    
    def test_mock_redis_fixture(self, mock_redis):
        """Test that mock Redis fixture works."""
        assert mock_redis is not None
        assert hasattr(mock_redis, 'get')
        assert hasattr(mock_redis, 'set')
        assert hasattr(mock_redis, 'delete')
        assert hasattr(mock_redis, 'publish')
        assert hasattr(mock_redis, 'pubsub')
    
    def test_mock_cloudinary_fixture(self, mock_cloudinary):
        """Test that mock Cloudinary fixture works."""
        assert mock_cloudinary is not None
        assert hasattr(mock_cloudinary, 'upload')
        assert hasattr(mock_cloudinary, 'destroy')
    
    def test_admin_auth_headers_fixture(self, admin_auth_headers):
        """Test that admin auth headers fixture works."""
        assert admin_auth_headers is not None
        assert "Cookie" in admin_auth_headers
        assert admin_auth_headers["Cookie"].startswith("token=")
    
    def test_sample_data_fixture(self, sample_data):
        """Test that sample data factory fixture works."""
        assert sample_data is not None
        user = sample_data.user()
        assert user["first_name"] == "John"
        assert user["role"] == "standard"
        
        doc = sample_data.document()
        assert doc["original_file_name"] == "test.pdf"
        assert doc["upload_status"] == "pending"
        
        chunk = sample_data.chunk()
        assert chunk["content"] == "Test chunk content"
    
    def test_service_mock_fixtures(self, mock_user_service, mock_document_service):
        """Test that service mock fixtures work."""
        assert mock_user_service is not None
        assert mock_document_service is not None
        assert hasattr(mock_user_service, 'is_valid_image_type')
        assert hasattr(mock_document_service, 'build_metadata')
    
    def test_orchestrator_mock_fixtures(self, mock_user_orchestrator, mock_document_orchestrator):
        """Test that orchestrator mock fixtures work."""
        assert mock_user_orchestrator is not None
        assert mock_document_orchestrator is not None
    
    def test_repository_mock_fixtures(self, mock_user_repository, mock_document_repository):
        """Test that repository mock fixtures work."""
        assert mock_user_repository is not None
        assert mock_document_repository is not None
    
    


class TestJWTTokenGeneration:
    """Test JWT token generation and verification."""
    
    def test_admin_token_has_correct_role(self, jwt_service, admin_token):
        """Test that admin token contains admin role."""
        decoded = jwt_service.verify(admin_token)
        assert decoded["role"] == "admin"
        assert decoded["provider_id"] == "admin-provider-id"
    
    def test_standard_token_has_correct_role(self, jwt_service, standard_token):
        """Test that standard token contains standard role."""
        decoded = jwt_service.verify(standard_token)
        assert decoded["role"] == "standard"
        assert decoded["provider_id"] == "standard-provider-id"
    
    def test_contributor_token_has_correct_role(self, jwt_service, contributor_token):
        """Test that contributor token contains contributor role."""
        decoded = jwt_service.verify(contributor_token)
        assert decoded["role"] == "contributor"
        assert decoded["provider_id"] == "contributor-provider-id"
    
    def test_expired_token_verification_fails(self, jwt_service, expired_token):
        """Test that expired token verification raises an exception."""
        with pytest.raises(Exception):
            jwt_service.verify(expired_token)
    
    def test_invalid_token_verification_fails(self, jwt_service):
        """Test that invalid token verification raises an exception."""
        with pytest.raises(Exception):
            jwt_service.verify("invalid.token.here")


class TestMockDatabase:
    """Test mock database functionality."""
    
    @pytest.mark.asyncio
    async def test_mock_db_connection(self, mock_db):
        """Test that mock database connection works."""
        async with mock_db.connection() as conn:
            assert conn is not None
            assert hasattr(conn, 'execute')
            assert hasattr(conn, 'commit')
            assert hasattr(conn, 'rollback')


class TestMockRedis:
    """Test mock Redis functionality."""
    
    @pytest.mark.asyncio
    async def test_mock_redis_basic_operations(self, mock_redis):
        """Test basic Redis operations."""
        # Test set/get
        await mock_redis.set("test_key", "test_value")
        value = await mock_redis.get("test_key")
        assert value == "test_value"
        
        # Test delete
        await mock_redis.delete("test_key")
        value = await mock_redis.get("test_key")
        assert value is None
    
    @pytest.mark.asyncio
    async def test_mock_redis_pubsub(self, mock_redis):
        """Test Redis pub/sub."""
        pubsub = mock_redis.pubsub()
        await pubsub.subscribe("test_channel")
        
        # Publish a message
        await mock_redis.publish("test_channel", "test_message")
        
        # Get the message
        message = await pubsub.get_message(timeout=1.0)
        assert message is not None
        assert message["channel"] == "test_channel"
        assert message["data"] == "test_message"
        
        await pubsub.close()


class TestMockCloudinary:
    """Test mock Cloudinary functionality."""
    
    @pytest.mark.asyncio
    async def test_mock_cloudinary_upload(self, mock_cloudinary):
        """Test Cloudinary upload."""
        result = await mock_cloudinary.upload(b"fake image data")
        assert "public_id" in result
        assert "secure_url" in result
        assert len(mock_cloudinary.uploaded) == 1
    
    @pytest.mark.asyncio
    async def test_mock_cloudinary_destroy(self, mock_cloudinary):
        """Test Cloudinary destroy."""
        # Upload first
        result = await mock_cloudinary.upload(b"fake image data")
        public_id = result["public_id"]
        
        # Destroy
        result = await mock_cloudinary.destroy(public_id)
        assert result["result"] == "ok"
        assert len(mock_cloudinary.removed) == 1
        assert mock_cloudinary.removed[0]["public_id"] == public_id