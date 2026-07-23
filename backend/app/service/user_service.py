from psycopg import AsyncConnection
from backend.app.database.database import Database
from backend.app.repository.user_repository import UserRepository


class UserService:
    def __init__(self, db: Database, user_repo: UserRepository):
        self._id = db
        self._user_repo = user_repo

    async def get_by_provider_id(
        self, provider_id: str, connection: AsyncConnection = None
    ):
        return await self._user_repo.get_by_provider_id(
            provider_id=provider_id, connection=connection
        )
