from uuid import UUID
from datetime import datetime
from psycopg import AsyncConnection
from backend.hukom_bot.database.database import Database
from backend.hukom_bot.schema.user_schema import (
    UserCreate,
    UserUpdate,
    UserSearch,
    UserGetByManyId,
    UserGetAll,
)
from backend.hukom_bot.repository.user_repository import UserRepository
from backend.hukom_bot.schema.mixin import DateRangeableMixin
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

    async def get_by_id(self, id: str, connection: AsyncConnection = None):
        return await self._user_repo.get_by_id(id=id, connection=connection)

    async def get_by_ids(
        self, param: UserGetByManyId, connection: AsyncConnection = None
    ):
        return await self._user_repo.get_by_many_id(param=param, connection=connection)

    async def get_by_provider_id(
        self, provider_id: str, connection: AsyncConnection = None
    ):
        return await self._user_repo.get_by_provider_id(
            provider_id=provider_id, connection=connection
        )

    async def get_most_upload_count(
        self, limit: int = 10, connection: AsyncConnection = None
    ):
        return await self._user_repo.get_most_upload_count(
            limit=limit, connection=connection
        )

    async def search(self, user: UserSearch, connection: AsyncConnection = None):
        return await self._user_repo.search(user=user, connection=connection)

    async def all(self, param: UserGetAll, connection: AsyncConnection = None):
        return await self._user_repo.all(param=param, connection=connection)

    async def count_all(
        self, date_range: DateRangeableMixin = None, connection: AsyncConnection = None
    ):
        return await self._user_repo.count_all(
            date_range=date_range, connection=connection
        )

    async def count_active(
        self, date_range: DateRangeableMixin = None, connection: AsyncConnection = None
    ):
        return await self._user_repo.count_active(
            date_range=date_range, connection=connection
        )

    async def count_inactive(
        self, date_range: DateRangeableMixin = None, connection: AsyncConnection = None
    ):
        return await self._user_repo.count_inactive(
            date_range=date_range, connection=connection
        )

    async def count_monthly_registration(
        self, year: int = datetime.now().year, connection: AsyncConnection = None
    ):
        return await self._user_repo.count_monthly_registration(
            year=year, connection=connection
        )

    async def count_registration(
        self, interval_days: int = 360, connection: AsyncConnection = None
    ):
        return await self._user_repo.count_registration(
            interval_days=interval_days, connection=connection
        )

    async def count_by_role(
        self, date_range: DateRangeableMixin = None, connection: AsyncConnection = None
    ):
        return await self._user_repo.count_by_role(
            date_range=date_range, connection=connection
        )

    async def delete(self, id: UUID, connection: AsyncConnection = None):
        await self._user_repo.delete(id=id, connection=connection)

    # Others ===============================

    def is_valid_image_type(self, contents: bytes) -> bool:
        return is_valid_file_type(
            content=contents, allowed_file_types=UserService.ALLOWED_IMAGE_TYPES
        )
