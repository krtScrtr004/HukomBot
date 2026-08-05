from psycopg import AsyncConnection
from backend.hukom_bot.database.database import Database
from backend.hukom_bot.schema.user_schema import UserCreate
from backend.hukom_bot.repository.user_repository import UserRepository


class UserService:
    def __init__(self, db: Database, user_repo: UserRepository):
        self._id = db
        self._user_repo = user_repo
        
    # Repository ===========================
        
    async def create(self, user: UserCreate, connection: AsyncConnection = None):
        return await self._user_repo.create(
            user=user, connection=connection
        )

    async def get_by_provider_id(
        self, provider_id: str, connection: AsyncConnection = None
    ):
        return await self._user_repo.get_by_provider_id(
            provider_id=provider_id, connection=connection
        )
