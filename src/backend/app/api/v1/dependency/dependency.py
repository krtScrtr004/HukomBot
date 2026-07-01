from backend.app.database.database import Database
from backend.app.service.document_service import DocumentService


def get_db() -> Database:
    return Database()


def get_document_service() -> DocumentService:
    return DocumentService(db=get_db())
