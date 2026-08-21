from psycopg import AsyncConnection
from backend.hukom_bot.database.database import Database
from backend.hukom_bot.schema.user_schema import UserCreate, UserUpdate
from backend.hukom_bot.repository.user_repository import UserRepository
from backend.hukom_bot.util.file_utilities import is_valid_file_type


class UserService:
    ALLOWED_IMAGE_TYPES = {"image/jpg", "image/jpeg", "image/png"}

    def __init__(self, db: Database, user_repo: UserRepository):
        self._db = db
        self._user_repo = user_repo

    # Repository ===========================

    async def create(self, user: UserCreate, connection: AsyncConnection = None):
        return await self._user_repo.create(user=user, connection=connection)

    async def update(self, user: UserUpdate, connection: AsyncConnection = None):
        await self._user_repo.update(user=user, connection=connection)
        
    async def get_by_id(
        self, id: str, connection: AsyncConnection = None
    ):
        return await self._user_repo.get_by_id(
            id=id, connection=connection
        )

    async def get_by_provider_id(
        self, provider_id: str, connection: AsyncConnection = None
    ):
        return await self._user_repo.get_by_provider_id(
            provider_id=provider_id, connection=connection
        )

    # Others ===============================

    def is_valid_image_type(self, contents: bytes) -> bool:
        return is_valid_file_type(
            content=contents, allowed_file_types=UserService.ALLOWED_IMAGE_TYPES
        )
