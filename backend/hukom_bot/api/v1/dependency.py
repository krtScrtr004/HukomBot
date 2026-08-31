import logging

from redis.asyncio import Redis
from fastapi import FastAPI, Request, Depends
from contextlib import asynccontextmanager

import backend.hukom_bot.core.redis as rd

from backend.hukom_bot.database.database import Database

from backend.hukom_bot.middleware.rate_limiter import RateLimiter

from backend.hukom_bot.enum.user_role import UserRole

from backend.hukom_bot.repository.case_analysis_session_repository import (
    CaseAnalysisSessionRepository,
)
from backend.hukom_bot.repository.case_analysis_version_repository import (
    CaseAnalysisVersionRepository,
)
from backend.hukom_bot.repository.case_analysis_version_fact_repository import (
    CaseAnalysisVersionFactRepository,
)
from backend.hukom_bot.repository.case_fact_repository import CaseFactRepository
from backend.hukom_bot.repository.case_fact_version_repository import (
    CaseFactVersionRepository,
)
from backend.hukom_bot.repository.chunk_repository import ChunkRepository
from backend.hukom_bot.repository.document_repository import DocumentRepository
from backend.hukom_bot.repository.revoked_token_repository import RevokedTokenRepository
from backend.hukom_bot.repository.user_repository import UserRepository

from backend.hukom_bot.schema.auth_schema import JWTPayload

from backend.hukom_bot.middleware.token_quota import TokenQuota

from backend.hukom_bot.service.auth_service import AuthService
from backend.hukom_bot.service.case_analysis_service import CaseAnalysisService
from backend.hukom_bot.service.chatbot_service import ChatbotService
from backend.hukom_bot.service.chunk_service import ChunkService
from backend.hukom_bot.service.document_service import DocumentService
from backend.hukom_bot.service.embedding_service import EmbeddingService
from backend.hukom_bot.service.jwt_service import JWTService
from backend.hukom_bot.service.google_service import GoogleService
from backend.hukom_bot.service.llm_service import LLMService
from backend.hukom_bot.service.reranker_service import RerankerService
from backend.hukom_bot.service.file_storage_service import FileStorageService
from backend.hukom_bot.service.jwt_service import JWTService
from backend.hukom_bot.service.revoked_token_service import RevokedTokenService
from backend.hukom_bot.service.user_service import UserService
from backend.hukom_bot.service.token_quota_service import TokenQuotaService

from backend.hukom_bot.orchistrator.admin_orchistrator import AdminOrchistrator
from backend.hukom_bot.orchistrator.document_orchistrator import DocumentOrchistrator
from backend.hukom_bot.orchistrator.case_analysis_orchistrator import (
    CaseAnalysisOrchistrator,
)
from backend.hukom_bot.orchistrator.user_orchistrator import UserOrchistrator

from backend.hukom_bot.exception.app_exception import UnauthorizedException

from backend.hukom_bot.util.utility import get_client_ip

logger = logging.getLogger(__name__)


# ============================================================================
# Lifespan & App State
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db = Database()
    logging.info("Database initialized successfully")

    app.state.redis = rd.get_redis()
    logging.info("Redis initialized successfully")

    app.state.embedding_service = EmbeddingService.initialize()
    logging.info("Embedding model loaded successfully")

    app.state.reranker_service = RerankerService.initialize()
    logging.info("Reranker model loaded successfully")

    await app.state.db.open()

    yield

    await app.state.db.close()
    logger.info("Database connection shutdown successfully")

    await rd.close_redis()
    logger.info("Redis connection shutdow successfully")


def get_db(request: Request) -> Database:
    return request.app.state.db


def get_redis(request: Request) -> Redis:
    return request.app.state.redis


# ============================================================================
# Infrastructure Services (app-state singletons)
# ============================================================================


def get_embedding_service(request: Request) -> EmbeddingService:
    return request.app.state.embedding_service.get_instance()


def get_reranker_service(request: Request) -> RerankerService:
    return request.app.state.reranker_service.get_instance()


# ============================================================================
# Stateless Services
# ============================================================================


def get_llm_service() -> LLMService:
    return LLMService()


def get_jwt_service() -> JWTService:
    return JWTService()


def get_file_storage_service() -> FileStorageService:
    return FileStorageService()


def get_google_service() -> GoogleService:
    return GoogleService()


# ============================================================================
# Repositories (Data Access)
# ============================================================================


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


def get_user_repository(db: Database = Depends(get_db)) -> UserRepository:
    return UserRepository(db=db)


def get_revoked_token_repository(
    db: Database = Depends(get_db),
) -> RevokedTokenRepository:
    return RevokedTokenRepository(db=db)


# ============================================================================
# Services (Business Logic)
# ============================================================================


def get_chunk_service(
    chunk_repo: ChunkRepository = Depends(get_chunk_repository),
) -> ChunkService:
    return ChunkService(chunk_repo=chunk_repo)


def get_chatbot_service(
    db: Database = Depends(get_db), llm_service: LLMService = Depends(get_llm_service)
) -> ChatbotService:
    return ChatbotService(
        db=db,
        llm_service=llm_service,
    )


def get_revoked_token_service(
    revoked_token_repo: RevokedTokenRepository = Depends(get_revoked_token_repository),
) -> RevokedTokenService:
    return RevokedTokenService(revoked_token_repo=revoked_token_repo)


def get_user_service(
    db: Database = Depends(get_db),
    user_repo: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(db=db, user_repo=user_repo)


def get_token_quota_service(redis: Redis = Depends(get_redis)) -> TokenQuotaService:
    return TokenQuotaService(redis=redis)


def get_auth_service(
    db: Database = Depends(get_db),
    user_service: UserRepository = Depends(get_user_service),
    revoked_token_service: RevokedTokenService = Depends(get_revoked_token_service),
    jwt_service: JWTService = Depends(get_jwt_service),
) -> AuthService:
    return AuthService(
        db=db,
        user_service=user_service,
        revoked_token_service=revoked_token_service,
        jwt_service=jwt_service,
    )


def get_case_analysis_service(
    db: Database = Depends(get_db),
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
    chunk_service: ChunkService = Depends(get_chunk_service),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    reranker_service: RerankerService = Depends(get_reranker_service),
) -> CaseAnalysisService:
    return CaseAnalysisService(
        db=db,
        case_fact_repo=case_fact_repo,
        case_fact_version_repo=case_fact_version_repo,
        case_analysis_session_repo=case_analysis_session_repo,
        case_analysis_version_repo=case_analysis_version_repo,
        case_analysis_version_fact_repo=case_analysis_version_fact_repo,
        chatbot_service=chatbot_service,
        chunk_service=chunk_service,
        embedding_service=embedding_service,
        reranker_service=reranker_service,
    )


def get_document_service(
    document_repo: DocumentRepository = Depends(get_document_repository),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    file_storage_service: FileStorageService = Depends(get_file_storage_service),
) -> DocumentService:
    return DocumentService(
        document_repo=document_repo,
        embedding_service=embedding_service,
        file_storage_service=file_storage_service,
    )


# ============================================================================
# Orchestrators (Application Layer)
# ============================================================================


def get_user_orchistrator(
    db: Database = Depends(get_db),
    user_service: UserService = Depends(get_user_service),
) -> UserOrchistrator:
    return UserOrchistrator(db=db, user_service=user_service)


def get_admin_orchistrator(
    db: Database = Depends(get_db),
    chunk_service: ChunkService = Depends(get_chunk_service),
    document_service: DocumentService = Depends(get_document_service),
    user_service: UserService = Depends(get_user_service),
) -> AdminOrchistrator:
    return AdminOrchistrator(
        db=db,
        chunk_service=chunk_service,
        document_service=document_service,
        user_service=user_service,
    )


def get_document_orchestrator(
    db: Database = Depends(get_db),
    chunk_service: ChunkService = Depends(get_chunk_service),
    document_service: DocumentService = Depends(get_document_service),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    file_storage_service: FileStorageService = Depends(get_file_storage_service),
    user_service: UserService = Depends(get_user_service),
) -> DocumentOrchistrator:
    return DocumentOrchistrator(
        db=db,
        chunk_service=chunk_service,
        document_service=document_service,
        embedding_service=embedding_service,
        file_storage_service=file_storage_service,
        user_service=user_service,
    )


def get_case_analysis_orchestrator(
    db: Database = Depends(get_db),
    case_analysis_service: CaseAnalysisService = Depends(get_case_analysis_service),
    token_quota_service: TokenQuotaService = Depends(get_token_quota_service),
) -> CaseAnalysisOrchistrator:
    return CaseAnalysisOrchistrator(
        db=db,
        case_analysis_service=case_analysis_service,
        token_quota_service=token_quota_service,
    )


# ============================================================================
# Authorization / Authentication Dependencies
# ============================================================================


async def verify_user(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        request_id = request.state.request_id

        token = request.cookies.get("token")
        if not token:
            raise UnauthorizedException

        # Check if valid token
        user = await auth_service.authenticate(request_id, token)
        return user
    except:
        auth_service.redirect_unauthorized(request=request, error_code="UNAUTHORIZED")


def rate_limit(limit: int = 10, window: int = 360):
    async def dependency(
        request: Request, jwt_service: JWTService = Depends(get_jwt_service)
    ):
        token = request.cookies.get("token")

        # If the user is authenticated, use their provider_id as the key; otherwise, use their IP address
        if token:
            try:
                decoded = jwt_service.verify(token)
                payload = JWTPayload.model_validate(decoded)
                if payload.provider_id:
                    key = f"user:{payload.provider_id}"
                else:
                    raise ValueError("Missing provider_id")
            except Exception:
                ip = get_client_ip(request)
                key = f"user:{ip}" if ip else "user:unknown"
        else:
            ip = get_client_ip(request)
            key = f"user:{ip}" if ip else "user:unknown"

        redis = request.app.state.redis
        rate_limiter = RateLimiter(redis=redis, limit=limit, window=window)
        await rate_limiter(key=key)

    return dependency


def require_role(*allowed_roles: UserRole):
    def dependency(
        request: Request, jwt_service: JWTService = Depends(get_jwt_service)
    ):
        try:
            token = request.cookies.get("token")
            if not token:
                raise

            decoded = jwt_service.verify(token)
            payload = JWTPayload.model_validate(decoded)
            if payload.role not in allowed_roles:
                raise UnauthorizedException(
                    message="You do not have permission to perform this action"
                )
        except Exception:
            raise UnauthorizedException

    return dependency


# ============================================================================
# Others
# ============================================================================


def get_ip(request: Request) -> str:
    return get_client_ip(request=request)
