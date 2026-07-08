from fastapi import FastAPI, Request, Depends
from contextlib import asynccontextmanager

from backend.app.database.database import Database
from backend.app.service.document_service import DocumentService
from backend.app.service.file_storage_service import FileStorageService


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db = Database()
    await app.state.db.open()
    yield
    await app.state.db.close()


def get_db(request: Request) -> Database:
    return request.app.state.db


def get_document_service(db: Database = Depends(get_db)) -> DocumentService:
    return DocumentService(db=db)


def get_file_storage_service() -> FileStorageService:
    return FileStorageService()
