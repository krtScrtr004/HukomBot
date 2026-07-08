import shutil

from uuid import UUID
from pathlib import Path
from fastapi import UploadFile
from fastapi.concurrency import run_in_threadpool


from backend.app.util.utility import get_project_root


class FileStorageService:
    def __init__(self):
        self.DATA_PATH = get_project_root() / "data"
        self.DATA_PATH.mkdir(parents=True, exist_ok=True)

    async def save_to_pending(
        self, upload_file_name: UUID, contents: bytes, suffix: str
    ):
        destination = self._pending_path() / f"{str(upload_file_name)}{suffix}"
        await run_in_threadpool(destination.write_bytes, contents)

        return destination

    async def delete_from_pending(self, file_name: str):
        destination = self._pending_path() / file_name
        destination.unlink()

    def _pending_path(self) -> Path:
        pending_path = self.DATA_PATH / "pending"
        pending_path.mkdir(parents=True, exist_ok=True)

        return pending_path
