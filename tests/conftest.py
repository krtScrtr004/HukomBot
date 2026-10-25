import os
import sys
from datetime import datetime, timedelta
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient
from fastapi import FastAPI

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.hukom_bot.main import app as fastapi_app
from backend.hukom_bot.schema.auth_schema import JWTPayload
from backend.hukom_bot.enum.user_role import UserRole
from backend.hukom_bot.service.jwt_service import JWTService
from backend.hukom_bot.core.settings import settings


# =============================================================================
# Test Configuration
# =============================================================================

os.environ.setdefault("DEBUG", "True")
os.environ.setdefault("BASE_PAGE_URL", "http://localhost:3000")
os.environ.setdefault("BASE_API_URL", "http://localhost:8000")
os.environ.setdefault("BASE_API_URL_V1", "http://localhost:8000/api/v1")

os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault("REDIS_PORT", "6379")

os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_NAME", "hukom_bot_test")
os.environ.setdefault("DB_USER", "test")
os.environ.setdefault("DB_PASSWORD", "test")

os.environ.setdefault("ADMIN_DASHBOARD_CH", "admin:dashboard")
os.environ.setdefault("ADMIN_USER_ANALYTICS_CH", "admin:users")
os.environ.setdefault("ADMIN_DOCUMENT_ANALYTICS_CH", "admin:documents")

os.environ.setdefault("JWT_SECRET", "test-secret-key-for-testing-only")
os.environ.setdefault("JWT_ALGO", "HS256")
os.environ.setdefault("JWT_ISS", "hukom-bot")
os.environ.setdefault("JWT_AUD", "hukom-bot-api")
os.environ.setdefault("JWT_EXP_IN_MIN", "60")

os.environ.setdefault("OAUTH_CLIENT_ID", "test-client-id")
os.environ.setdefault("OAUTH_CLIENT_SECRET", "test-client-secret")

os.environ.setdefault("GOOGLE_OAUTH_REDIRECT_URI", "http://localhost:8000/api/v1/auth/google/callback")
os.environ.setdefault("GOOGLE_AUTH_URL", "https://accounts.google.com/o/oauth2/auth")
os.environ.setdefault("GOOGLE_TOKEN_URL", "https://oauth2.googleapis.com/token")

os.environ.setdefault("GEMINI_API_KEY", "test-gemini-key")
os.environ.setdefault("GEMINI_MODEL", "gemini-pro")
os.environ.setdefault("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com")

os.environ.setdefault("OPEN_ROUTER_API_KEY", "test-openrouter-key")
os.environ.setdefault("OPEN_ROUTER_MODEL", "openrouter-model")
os.environ.setdefault("OPEN_ROUTER_BASE_URL", "https://openrouter.ai/api/v1")

os.environ.setdefault("NVIDIA_API_KEY", "test-nvidia-key")
os.environ.setdefault("NVIDIA_MODEL", "nvidia-model")
os.environ.setdefault("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")

os.environ.setdefault("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
os.environ.setdefault("EMBEDDING_DEVICE_CPU", "cpu")
os.environ.setdefault("EMBEDDING_DEVICE_GPU", "cuda")

os.environ.setdefault("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
os.environ.setdefault("RERANKER_DEVICE_CPU", "cpu")
os.environ.setdefault("RERANKER_DEVICE_GPU", "cuda")

os.environ.setdefault("TOKEN_QUOTA_DAILY", "10000")
os.environ.setdefault("TOKEN_QUOTA_WINDOW", "86400")

os.environ.setdefault("CLOUDINARY_NAME", "test-cloudinary")
os.environ.setdefault("CLOUDINARY_API_KEY", "test-cloudinary-key")
os.environ.setdefault("CLOUDINARY_SECRET", "test-cloudinary-secret")


# =============================================================================
# Session-scoped fixtures
# =============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def jwt_service() -> JWTService:
    """Provide a JWTService instance for token encoding/verification."""
    return JWTService()


@pytest.fixture(scope="session")
def admin_jwt_payload() -> JWTPayload:
    """Create a JWT payload for an admin user."""
    return JWTPayload(
        jti=uuid4(),
        provider_id="admin-provider-id",
        role=UserRole.ADMIN,
    )


@pytest.fixture(scope="session")
def standard_jwt_payload() -> JWTPayload:
    """Create a JWT payload for a standard user."""
    return JWTPayload(
        jti=uuid4(),
        provider_id="standard-provider-id",
        role=UserRole.STANDARD,
    )


@pytest.fixture(scope="session")
def contributor_jwt_payload() -> JWTPayload:
    """Create a JWT payload for a contributor user."""
    return JWTPayload(
        jti=uuid4(),
        provider_id="contributor-provider-id",
        role=UserRole.CONTRIBUTOR,
    )


@pytest.fixture(scope="session")
def admin_token(jwt_service: JWTService, admin_jwt_payload: JWTPayload) -> str:
    """Generate a valid admin JWT token."""
    return jwt_service.encode(admin_jwt_payload)


@pytest.fixture(scope="session")
def standard_token(jwt_service: JWTService, standard_jwt_payload: JWTPayload) -> str:
    """Generate a valid standard user JWT token."""
    return jwt_service.encode(standard_jwt_payload)


@pytest.fixture(scope="session")
def contributor_token(jwt_service: JWTService, contributor_jwt_payload: JWTPayload) -> str:
    """Generate a valid contributor JWT token."""
    return jwt_service.encode(contributor_jwt_payload)


@pytest.fixture(scope="session")
def expired_token(jwt_service: JWTService) -> str:
    """Generate an expired JWT token."""
    expired_payload = JWTPayload(
        jti=uuid4(),
        provider_id="expired-provider-id",
        role=UserRole.STANDARD,
        exp=int((datetime.now() - timedelta(hours=1)).timestamp()),
    )
    return jwt_service.encode(expired_payload)


# =============================================================================
# Mock Database Fixtures
# =============================================================================

class MockDatabase:
    """Mock database that simulates psycopg pool behavior."""
    
    def __init__(self):
        self._pool = MagicMock()
        self._conn = AsyncMock()
        self._cursor = AsyncMock()
        # Setup connection context manager
        self._pool.connection.return_value.__aenter__ = AsyncMock(return_value=self._conn)
        self._pool.connection.return_value.__aexit__ = AsyncMock(return_value=None)
        # Setup cursor context manager - cursor() returns an async context manager
        cursor_cm = MagicMock()
        cursor_cm.__aenter__ = AsyncMock(return_value=self._cursor)
        cursor_cm.__aexit__ = AsyncMock(return_value=None)
        self._conn.cursor = AsyncMock(return_value=cursor_cm)
        self._cursor.fetchone = AsyncMock(return_value=None)
        self._cursor.fetchall = AsyncMock(return_value=[])
        self._cursor.execute = AsyncMock()
        self._conn.execute = AsyncMock()
        self._conn.commit = AsyncMock()
        self._conn.rollback = AsyncMock()
    
    async def open(self):
        pass
    
    async def close(self):
        pass
    
    def connection(self):
        return self._pool.connection()
    
    @property
    def cursor(self):
        return self._cursor
    
    @property
    def conn(self):
        return self._conn


@pytest.fixture
def mock_db() -> MockDatabase:
    """Provide a mock database instance."""
    return MockDatabase()


# =============================================================================
# Mock Redis Fixtures
# =============================================================================

class MockRedis:
    """Mock Redis client for testing."""
    
    def __init__(self):
        self._data = {}
        self._pubsub_channels = {}
        self._subscribers = {}
    
    async def get(self, key: str):
        return self._data.get(key)
    
    async def set(self, key: str, value: str, ex: int = None):
        self._data[key] = value
        return True
    
    async def delete(self, *keys: str):
        for key in keys:
            self._data.pop(key, None)
        return len(keys)
    
    async def exists(self, key: str):
        return key in self._data
    
    async def incr(self, key: str):
        val = int(self._data.get(key, 0)) + 1
        self._data[key] = str(val)
        return val
    
    async def expire(self, key: str, seconds: int):
        return True
    
    async def ttl(self, key: str):
        return -1 if key in self._data else -2
    
    def pubsub(self):
        return MockPubSub(self)
    
    async def publish(self, channel: str, message: str):
        if channel in self._pubsub_channels:
            for sub in self._pubsub_channels[channel]:
                await sub.put(message)
        return len(self._pubsub_channels.get(channel, []))
    
    async def close(self):
        pass
    
    async def ping(self):
        return True


class MockPubSub:
    """Mock Redis PubSub for testing."""
    
    def __init__(self, redis: MockRedis):
        self._redis = redis
        self._channels = {}
        self._queue = []
    
    async def subscribe(self, *channels: str):
        for channel in channels:
            if channel not in self._redis._pubsub_channels:
                self._redis._pubsub_channels[channel] = []
            import asyncio
            queue = asyncio.Queue()
            self._redis._pubsub_channels[channel].append(queue)
            self._channels[channel] = queue
    
    async def unsubscribe(self, *channels: str):
        for channel in channels:
            if channel in self._redis._pubsub_channels:
                self._redis._pubsub_channels[channel] = [
                    q for q in self._redis._pubsub_channels[channel] 
                    if q != self._channels.get(channel)
                ]
            self._channels.pop(channel, None)
    
    async def get_message(self, timeout: float = None, ignore_subscribe_messages: bool = False):
        import asyncio
        for channel, queue in self._channels.items():
            try:
                message = await asyncio.wait_for(queue.get(), timeout=timeout or 0.1)
                return {
                    "type": "message",
                    "channel": channel,
                    "data": message,
                }
            except asyncio.TimeoutError:
                continue
        return None
    
    async def close(self):
        await self.unsubscribe(*self._channels.keys())


@pytest.fixture
def mock_redis() -> MockRedis:
    """Provide a mock Redis instance."""
    return MockRedis()


# =============================================================================
# Mock Cloudinary Fixtures
# =============================================================================

class MockCloudinary:
    """Mock Cloudinary upload/remove for testing."""
    
    def __init__(self):
        self.uploaded = {}
        self.removed = []
    
    async def upload(self, file, **kwargs):
        public_id = f"test_{uuid4().hex[:8]}"
        self.uploaded[public_id] = {"file": file, "kwargs": kwargs}
        return {
            "public_id": public_id,
            "secure_url": f"https://res.cloudinary.com/test/image/upload/{public_id}",
            "format": "jpg",
            "width": 100,
            "height": 100,
        }
    
    async def destroy(self, public_id: str, **kwargs):
        self.removed.append({"public_id": public_id, "kwargs": kwargs})
        return {"result": "ok"}


@pytest.fixture
def mock_cloudinary() -> MockCloudinary:
    """Provide a mock Cloudinary instance."""
    return MockCloudinary()


# =============================================================================
# FastAPI Test Client Fixtures
# =============================================================================

@pytest.fixture
def app() -> FastAPI:
    """Provide the FastAPI app instance."""
    return fastapi_app


@pytest_asyncio.fixture
async def async_client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Provide an async HTTP client for testing API endpoints."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# =============================================================================
# Authentication Helper Fixtures
# =============================================================================

@pytest.fixture
def admin_auth_headers(admin_token: str) -> dict:
    """Headers with admin authentication cookie."""
    return {"Cookie": f"token={admin_token}"}


@pytest.fixture
def standard_auth_headers(standard_token: str) -> dict:
    """Headers with standard user authentication cookie."""
    return {"Cookie": f"token={standard_token}"}


@pytest.fixture
def contributor_auth_headers(contributor_token: str) -> dict:
    """Headers with contributor authentication cookie."""
    return {"Cookie": f"token={contributor_token}"}


@pytest.fixture
def expired_auth_headers(expired_token: str) -> dict:
    """Headers with expired authentication cookie."""
    return {"Cookie": f"token={expired_token}"}


# =============================================================================
# Sample Data Factories
# =============================================================================

class SampleDataFactory:
    """Factory for creating sample test data."""
    
    @staticmethod
    def user(
        id: str = None,
        provider_id: str = None,
        first_name: str = "John",
        last_name: str = "Doe",
        email: str = "john.doe@example.com",
        role: UserRole = UserRole.STANDARD,
        is_active: bool = True,
        profile_picture: str = None,
        upload_count: int = 0,
        created_at: datetime = None,
        updated_at: datetime = None,
    ) -> dict:
        now = datetime.now()
        return {
            "id": id or str(uuid4()),
            "provider_id": provider_id or f"provider_{uuid4().hex[:8]}",
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "role": role,
            "is_active": is_active,
            "profile_picture": profile_picture,
            "upload_count": upload_count,
            "created_at": created_at or now,
            "updated_at": updated_at or now,
        }
    
    @staticmethod
    def document(
        id: str = None,
        uploader_id: str = None,
        original_file_name: str = "test.pdf",
        document_type: str = "statute",
        upload_status: str = "pending",
        file_size: int = 1024,
        digest: str = None,
        rejection_message: str = None,
        upload_error: str = None,
        created_at: datetime = None,
        updated_at: datetime = None,
    ) -> dict:
        now = datetime.now()
        return {
            "id": id or str(uuid4()),
            "uploader_id": uploader_id or str(uuid4()),
            "original_file_name": original_file_name,
            "document_type": document_type,
            "upload_status": upload_status,
            "file_size": file_size,
            "digest": digest or "a" * 64,
            "rejection_message": rejection_message,
            "upload_error": upload_error,
            "created_at": created_at or now,
            "updated_at": updated_at or now,
        }
    
    @staticmethod
    def chunk(
        id: str = None,
        document_id: str = None,
        chunk_index: int = 0,
        content: str = "Test chunk content",
        embedding: list = None,
        created_at: datetime = None,
    ) -> dict:
        now = datetime.now()
        return {
            "id": id or str(uuid4()),
            "document_id": document_id or str(uuid4()),
            "chunk_index": chunk_index,
            "content": content,
            "embedding": embedding or [0.1] * 384,
            "created_at": created_at or now,
        }


@pytest.fixture
def sample_data() -> SampleDataFactory:
    """Provide sample data factory."""
    return SampleDataFactory()


# =============================================================================
# Service Mock Fixtures
# =============================================================================

@pytest.fixture
def mock_user_service() -> MagicMock:
    """Provide a mocked UserService."""
    service = MagicMock()
    service.is_valid_image_type = MagicMock(return_value=True)
    service.count_active = AsyncMock(return_value=10)
    service.count_inactive = AsyncMock(return_value=2)
    service.count_by_role = AsyncMock(return_value={"admin": 1, "standard": 8, "contributor": 3})
    service.count_monthly_registration = AsyncMock(return_value=[{"month": "2024-01", "count": 5}])
    service.delete = AsyncMock(return_value=True)
    return service


@pytest.fixture
def mock_document_service() -> MagicMock:
    """Provide a mocked DocumentService."""
    service = MagicMock()
    service.is_valid_file_type = MagicMock(return_value=True)
    service.build_metadata = MagicMock(return_value={
        "file_path": "/test/path/test.pdf",
        "upload_file_name": "test.pdf",
        "file_extension": ".pdf",
        "digest": "a" * 64,
    })
    service.get_upload_status = AsyncMock(return_value="pending")
    service.delete = AsyncMock(return_value=True)
    service.delete_many = AsyncMock(return_value=True)
    return service


@pytest.fixture
def mock_pubsub_service() -> MagicMock:
    """Provide a mocked PubsubService."""
    service = MagicMock()
    service.publish = AsyncMock(return_value=1)
    service.get_message = AsyncMock(return_value=None)
    service.subscribe = AsyncMock()
    service.unsubscribe = AsyncMock()
    service.close = AsyncMock()
    return service


@pytest.fixture
def mock_file_storage_service() -> MagicMock:
    """Provide a mocked FileStorageService."""
    service = MagicMock()
    service.save_to_pending = AsyncMock(return_value="/tmp/test.pdf")
    service.get_pending_file = MagicMock(return_value="/tmp/test.pdf")
    service.delete_from_pending = AsyncMock(return_value=True)
    service.read_file = AsyncMock(return_value=b"test content")
    return service


@pytest.fixture
def mock_chunk_service() -> MagicMock:
    """Provide a mocked ChunkService."""
    service = MagicMock()
    service.extract_text_to_chunks = AsyncMock(return_value=[
        {"content": "Chunk 1", "embedding": [0.1] * 384},
        {"content": "Chunk 2", "embedding": [0.2] * 384},
    ])
    return service


# =============================================================================
# Orchestrator Mock Fixtures
# =============================================================================

@pytest.fixture
def mock_user_orchestrator() -> MagicMock:
    """Provide a mocked UserOrchistrator."""
    orch = MagicMock()
    orch.update_profile = AsyncMock(return_value={"success": True})
    orch.update_user = AsyncMock(return_value={"success": True})
    orch.upload_profile_picture = AsyncMock(return_value={"success": True})
    orch.delete_user = AsyncMock(return_value={"success": True})
    return orch


@pytest.fixture
def mock_document_orchestrator() -> MagicMock:
    """Provide a mocked DocumentOrchistrator."""
    orch = MagicMock()
    orch.approve_document_upload = AsyncMock(return_value={"success": True})
    orch.process_document_pdf_upload = AsyncMock(return_value={"success": True})
    orch.update_pipeline = AsyncMock(return_value={"success": True})
    orch.search_pipeline = AsyncMock(return_value={"items": [], "total": 0})
    return orch


@pytest.fixture
def mock_admin_orchestrator() -> MagicMock:
    """Provide a mocked AdminOrchistrator."""
    orch = MagicMock()
    orch.get_dashboard_data = AsyncMock(return_value={
        "total_users": 100,
        "active_users": 80,
        "total_documents": 500,
        "pending_documents": 10,
    })
    orch.get_user_analytics = AsyncMock(return_value={
        "total_users": 100,
        "by_role": {"admin": 1, "standard": 80, "contributor": 19},
        "monthly_registrations": [],
    })
    orch.get_document_analytics = AsyncMock(return_value={
        "total_count": 500,
        "status_count": {"pending": 10, "completed": 450},
        "type_count": {"statute": 300, "contract": 200},
        "monthly_upload_count": {},
    })
    return orch


# =============================================================================
# Repository Mock Fixtures
# =============================================================================

@pytest.fixture
def mock_user_repository() -> MagicMock:
    """Provide a mocked UserRepository."""
    repo = MagicMock()
    repo.create = AsyncMock(return_value={"id": str(uuid4())})
    repo.get_by_id = AsyncMock(return_value=None)
    repo.get_by_many_id = AsyncMock(return_value=[])
    repo.update = AsyncMock(return_value=True)
    repo.delete = AsyncMock(return_value=True)
    repo.count_by_role = AsyncMock(return_value={"admin": 1, "standard": 10})
    repo.search = AsyncMock(return_value=[])
    return repo


@pytest.fixture
def mock_document_repository() -> MagicMock:
    """Provide a mocked DocumentRepository."""
    repo = MagicMock()
    repo.create = AsyncMock(return_value={"id": str(uuid4())})
    repo.get_by_id = AsyncMock(return_value=None)
    repo.get_upload_status_by_id = AsyncMock(return_value="pending")
    repo.update = AsyncMock(return_value=True)
    repo.delete = AsyncMock(return_value=True)
    repo.delete_many = AsyncMock(return_value=True)
    repo.count_by_upload_status = AsyncMock(return_value={"pending": 5, "completed": 10})
    repo.count_weekly = AsyncMock(return_value=[{"week": "2024-01", "count": 3}])
    repo.count_by_document_type = AsyncMock(return_value={"statute": 5, "contract": 3})
    repo.search = AsyncMock(return_value=[])
    return repo


# =============================================================================
# Utility Fixtures
# =============================================================================

@pytest.fixture
def mock_settings(monkeypatch):
    """Patch settings with test values."""
    test_settings = {
        "DEBUG": True,
        "BASE_PAGE_URL": "http://localhost:3000",
        "BASE_API_URL": "http://localhost:8000",
        "BASE_API_URL_V1": "http://localhost:8000/api/v1",
        "JWT_SECRET": "test-secret-key-for-testing-only",
        "JWT_ALGO": "HS256",
        "JWT_ISS": "hukom-bot",
        "JWT_AUD": "hukom-bot-api",
        "JWT_EXP_IN_MIN": 60,
        "TOKEN_QUOTA_DAILY": 10000,
        "TOKEN_QUOTA_WINDOW": 86400,
    }
    for key, value in test_settings.items():
        monkeypatch.setattr(settings, key, value)
    return settings


# =============================================================================
# Pytest Configuration
# =============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "api: API endpoint tests")
    config.addinivalue_line("markers", "slow: Slow running tests")


def pytest_collection_modifyitems(config, items):
    """Auto-mark tests based on their path."""
    for item in items:
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "api" in str(item.fspath):
            item.add_marker(pytest.mark.api)