import logging

from fastapi import FastAPI, Request, Depends
from contextlib import asynccontextmanager

from backend.app.database.database import Database
from backend.app.service.chatbot_service import ChatbotService
from backend.app.service.document_service import DocumentService
from backend.app.service.embed_service import EmbedService
from backend.app.service.reranker_service import RerankService
from backend.app.service.file_storage_service import FileStorageService

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db = Database()
    logging.info("Database initialized successfully")
    
    app.state.embed_service = EmbedService.initialize()
    logging.info("Embedding model loaded successfully")
    
    app.state.rerank_service = RerankService.initialize()
    logging.info("Reranker model loaded successfully")
    
    await app.state.db.open()
    yield
    await app.state.db.close()


def get_db(request: Request) -> Database:
    return request.app.state.db

def get_embed_service(request: Request) -> EmbedService:
    return request.app.state.embed_service.get_instance()

def get_rerank_service(request: Request) -> RerankService:
    return request.app.state.rerank_service.get_instance()


def get_chatbot_service(
    db: Database = Depends(get_db),
    embed_service: EmbedService = Depends(get_embed_service),
    rerank_service: RerankService = Depends(get_rerank_service)
) -> ChatbotService:
    return ChatbotService(db, embed_service, rerank_service)


def get_document_service(db: Database = Depends(get_db)) -> DocumentService:
    return DocumentService(db=db)


def get_file_storage_service() -> FileStorageService:
    return FileStorageService()
