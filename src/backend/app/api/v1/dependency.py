import logging

from fastapi import FastAPI, Request, Depends
from contextlib import asynccontextmanager

from backend.app.database.database import Database
from backend.app.service.case_analysis_service import CaseAnalysisService
from backend.app.service.document_service import DocumentService
from backend.app.service.embedding_service import EmbeddingService
from backend.app.service.reranker_service import RerankerService
from backend.app.service.file_storage_service import FileStorageService

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db = Database()
    logging.info("Database initialized successfully")
    
    app.state.embedding_service = EmbeddingService.initialize()
    logging.info("Embedding model loaded successfully")
    
    app.state.reranker_service = RerankerService.initialize()
    logging.info("Reranker model loaded successfully")
    
    await app.state.db.open()
    yield
    await app.state.db.close()


def get_db(request: Request) -> Database:
    return request.app.state.db

def get_embedding_service(request: Request) -> EmbeddingService:
    return request.app.state.embedding_service.get_instance()

def get_reranker_service(request: Request) -> RerankerService:
    return request.app.state.reranker_service.get_instance()


def get_case_analysis_service(
    db: Database = Depends(get_db),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    reranker_service: RerankerService = Depends(get_reranker_service)
) -> CaseAnalysisService:
    return CaseAnalysisService(db, embedding_service, reranker_service)


def get_document_service(db: Database = Depends(get_db)) -> DocumentService:
    return DocumentService(db=db)


def get_file_storage_service() -> FileStorageService:
    return FileStorageService()
