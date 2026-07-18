import logging

from fastapi import FastAPI, Request, Depends
from contextlib import asynccontextmanager

from backend.app.database.database import Database

from backend.app.repository.case_analysis_session_repository import (
    CaseAnalysisSessionRepository,
)
from backend.app.repository.case_analysis_version_repository import (
    CaseAnalysisVersionRepository,
)
from backend.app.repository.case_analysis_version_fact_repository import (
    CaseAnalysisVersionFactRepository,
)
from backend.app.repository.case_fact_repository import CaseFactRepository
from backend.app.repository.case_fact_version_repository import (
    CaseFactVersionRepository,
)
from backend.app.repository.chunk_repository import ChunkRepository
from backend.app.repository.document_repository import DocumentRepository

from backend.app.service.chatbot_service import ChatbotService
from backend.app.service.case_analysis_service import CaseAnalysisService
from backend.app.service.document_service import DocumentService
from backend.app.service.embedding_service import EmbeddingService
from backend.app.service.google_oauth_service import GoogleOAuthService
from backend.app.service.llm_service import LLMService
from backend.app.service.reranker_service import RerankerService
from backend.app.service.file_storage_service import FileStorageService

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db = Database()
    logging.info("Database initialized successfully")

    # app.state.embedding_service = EmbeddingService.initialize()
    # logging.info("Embedding model loaded successfully")

    # app.state.reranker_service = RerankerService.initialize()
    # logging.info("Reranker model loaded successfully")

    await app.state.db.open()
    yield
    await app.state.db.close()


def get_db(request: Request) -> Database:
    return request.app.state.db


def get_embedding_service(request: Request) -> EmbeddingService:
    return request.app.state.embedding_service.get_instance()


def get_google_oauth_service() -> GoogleOAuthService:
    return GoogleOAuthService()


def get_llm_service() -> LLMService:
    return LLMService()


def get_reranker_service(request: Request) -> RerankerService:
    return request.app.state.reranker_service.get_instance()


def get_file_storage_service() -> FileStorageService:
    return FileStorageService()


def get_chunk_repository(db: Database = Depends(get_db)) -> ChunkRepository:
    return ChunkRepository(db=db)


def get_case_fact_repository(db: Database = Depends(get_db)) -> CaseFactRepository:
    return CaseFactRepository(db=db)


def get_case_fact_version_repository(
    db: Database = Depends(get_db),
) -> CaseFactVersionRepository:
    return CaseFactVersionRepository(db=db)


def get_case_analysis_session_repository(
    db: Database = Depends(get_db),
) -> CaseAnalysisSessionRepository:
    return CaseAnalysisSessionRepository(db=db)


def get_case_analysis_version_repository(
    db: Database = Depends(get_db),
) -> CaseAnalysisVersionRepository:
    return CaseAnalysisVersionRepository(db=db)


def get_case_analysis_version_fact_repository(
    db: Database = Depends(get_db),
) -> CaseAnalysisVersionFactRepository:
    return CaseAnalysisVersionFactRepository(db=db)


def get_document_repository(db: Database = Depends(get_db)) -> DocumentRepository:
    return DocumentRepository(db=db)


def get_chatbot_service(
    db: Database = Depends(get_db), llm_service: LLMService = Depends(get_llm_service)
) -> ChatbotService:
    return ChatbotService(
        db=db,
        llm_service=llm_service,
    )


def get_case_analysis_service(
    db: Database = Depends(get_db),
    chunk_repo: ChunkRepository = Depends(get_chunk_repository),
    case_fact_repo: CaseFactRepository = Depends(get_case_fact_repository),
    case_fact_version_repo: CaseFactVersionRepository = Depends(
        get_case_fact_version_repository
    ),
    case_analysis_session_repo: CaseAnalysisSessionRepository = Depends(
        get_case_analysis_session_repository
    ),
    case_analysis_version_repo: CaseAnalysisVersionRepository = Depends(
        get_case_analysis_version_repository
    ),
    case_analysis_version_fact_repo: CaseAnalysisVersionFactRepository = Depends(
        get_case_analysis_version_fact_repository
    ),
    chatbot_service: ChatbotService = Depends(get_chatbot_service),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    reranker_service: RerankerService = Depends(get_reranker_service),
) -> CaseAnalysisService:
    return CaseAnalysisService(
        db=db,
        chunk_repo=chunk_repo,
        case_fact_repo=case_fact_repo,
        case_fact_version_repo=case_fact_version_repo,
        case_analysis_session_repo=case_analysis_session_repo,
        case_analysis_version_repo=case_analysis_version_repo,
        case_analysis_version_fact_repo=case_analysis_version_fact_repo,
        chatbot_service=chatbot_service,
        embedding_service=embedding_service,
        reranker_service=reranker_service,
    )


def get_document_service(
    db: Database = Depends(get_db),
    document_repo: DocumentRepository = Depends(get_document_repository),
    chunk_repo: ChunkRepository = Depends(get_chunk_repository),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    file_storage_service: FileStorageService = Depends(get_file_storage_service),
) -> DocumentService:
    return DocumentService(
        db=db,
        document_repo=document_repo,
        chunk_repo=chunk_repo,
        embedding_service=embedding_service,
        file_storage_service=file_storage_service,
    )
