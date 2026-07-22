import logging
from uuid import UUID
from psycopg import AsyncConnection
from fastapi.concurrency import run_in_threadpool

from backend.app.database.database import Database
from backend.app.model.chunk_model import Chunk
from backend.app.model.case_analysis_model import *
from backend.app.schema.chunk_schema import ChunkSearchKeyword, ChunkSearchVector
from backend.app.schema.case_analysis_schema import *
from backend.app.service.chatbot_service import ChatbotService
from backend.app.service.chunk_service import ChunkService
from backend.app.service.embedding_service import EmbeddingService
from backend.app.service.reranker_service import RerankerService
from backend.app.repository.case_fact_repository import CaseFactRepository
from backend.app.repository.case_fact_version_repository import (
    CaseFactVersionRepository,
)
from backend.app.repository.case_analysis_version_repository import (
    CaseAnalysisVersionRepository,
)
from backend.app.repository.case_analysis_version_fact_repository import (
    CaseAnalysisVersionFactRepository,
)
from backend.app.util.case_analysis_version_caster import CaseAnalysisVersionCaster
from backend.app.exception.app_exception import NotFoundException
from backend.app.exception.chat_exception import ChatException

logger = logging.getLogger(__name__)


class CaseAnalysisService:
    def __init__(
        self,
        db: Database,
        case_fact_repo: CaseFactRepository,
        case_fact_version_repo: CaseFactVersionRepository,
        case_analysis_session_repo: CaseAnalysisVersionRepository,
        case_analysis_version_repo: CaseAnalysisVersionRepository,
        case_analysis_version_fact_repo: CaseAnalysisVersionFactRepository,
        chatbot_service: ChatbotService,
        chunk_service: ChunkService,
        embedding_service: EmbeddingService,
        reranker_service: RerankerService,
    ):
        self._db = db

        self._case_fact_repo = case_fact_repo
        self._case_fact_version_repo = case_fact_version_repo
        self._case_analysis_session_repo = case_analysis_session_repo
        self._case_analysis_version_repo = case_analysis_version_repo
        self._case_analysis_version_fact_repo = case_analysis_version_fact_repo

        self._chunk_service = chunk_service
        self._chatbot_service = chatbot_service
        self._embedding_service = embedding_service
        self._reranker_service = reranker_service

    # Repository ================

    async def create_session(
        self,
        session: CaseAnalysisSessionCreate,
        connection: AsyncConnection = None,
    ):
        return await self._case_analysis_session_repo.create(session, connection)

    async def create_facts(
        self,
        session_id: UUID,
        facts: list[str],
        connection: AsyncConnection = None,
    ):
        return await self._case_fact_repo.create_many(
            [CaseFactCreate(case_analysis_session_id=session_id) for _ in facts],
            connection,
        )

    async def create_fact_versions(
        self,
        version_number: int,
        raw_facts: list[str],
        obj_facts: list[CaseFact],
        connection: AsyncConnection = None,
    ):
        return await self._case_fact_version_repo.create_many(
            [
                CaseFactVersionCreate(
                    case_fact_id=fact.id,
                    version_number=version_number,
                    fact=raw_facts[i],
                    is_deleted=False,
                )
                for i, fact in enumerate(obj_facts)
            ],
            connection,
        )

    async def create_analysis_version(
        self,
        session_id: UUID,
        version_number: int,
        answer: str,
        connection: AsyncConnection = None,
    ):
        return await self._case_analysis_version_repo.create(
            CaseAnalysisVersionCreate(
                case_analysis_session_id=session_id,
                version_number=version_number,
                answer=answer,
            ),
            connection,
        )

    async def create_analysis_version_fact(
        self,
        facts_count: int,
        analysis_version_id: UUID,
        facts: list[CaseFactVersion],
        connection: AsyncConnection = None,
    ):
        return await self._case_analysis_version_fact_repo.create_many(
            [
                CaseAnalysisVersionFactCreate(
                    case_analysis_version_id=analysis_version_id,
                    case_fact_version_id=facts[i].id,
                )
                for i in range(facts_count)
            ],
            connection,
        )

    async def create_updated_fact_versions(
        self,
        case_fact_versions: list[CaseFactVersionCreate],
        connection: AsyncConnection = None,
    ):
        return await self._case_fact_version_repo.create_updated_many(
            case_fact_versions,
            connection,
        )

    async def update_case_fact_versions(
        self,
        fact_versions: list[CaseFactVersionUpdate],
        connection: AsyncConnection = None,
    ):
        await self._case_fact_version_repo.update_many(fact_versions, connection)

    async def delete_case_facts(
        self, ids: list[UUID], connection: AsyncConnection = None
    ):
        await self._case_fact_repo.delete_many(ids, connection)

    async def delete_case_fact_versions(
        self, ids: list[UUID], connection: AsyncConnection = None
    ):
        await self._case_fact_version_repo.delete_many(ids, connection)

    async def get_latest_analysis_version_by_session_id(self, session_id: UUID):
        return await self._case_analysis_version_repo.get_latest_by_session_id(
            session_id
        )

    async def get_latest_fact_version_by_session_id(
        self, session_id: UUID, connection: AsyncConnection = None
    ):
        return await self._case_fact_version_repo.get_latest_by_session_id(
            CaseFactVersionGetBySessionId(case_analysis_session_id=session_id),
            connection,
        )

    # async def get_case_analysis(self, param:  connection: AsyncConnection = None):
    #     return await self._case_analysis_version_repo.get_by_version_number(param)

    # Others ====================

    async def ensure_valid_session_id(self, case_analysis_session_id: UUID):
        is_session_existing = await self._case_analysis_session_repo.is_existing_by_id(
            case_analysis_session_id
        )
        if not is_session_existing:
            raise NotFoundException(
                code="CASE_ANALYSIS_NOT_FOUND", message="Case analysis not found"
            )

    async def get_by_version(self, case_analysis_session_id: UUID, version_number: int):
        await self.ensure_valid_session_id(case_analysis_session_id)

        param = CaseAnalysisGetByVersionNumber(
            case_analysis_session_id=case_analysis_session_id,
            version_number=version_number,
        )

        # Get case facts
        case_fact_versions = await self._case_fact_version_repo.get_by_version_number(
            param
        )
        if not case_fact_versions:
            raise NotFoundException(
                code="CASE_FACT_VERSION_NOT_FOUND",
                messaege="Case analysis fetch failed",
                details=[
                    f"No case fact versions found for case analysis session {case_analysis_session_id} version {version_number}"
                ],
            )

        case_analysis_version = (
            await self._case_analysis_version_repo.get_by_version_number(param)
        )
        if not case_analysis_version:
            raise NotFoundException(
                code="CASE_ANALYSIS_NOT_FOUND",
                messaege="Case analysis fetch failed",
                details=[
                    f"No case analysis versions found for session {case_analysis_session_id} version {version_number}"
                ],
            )

        case_facts = [
            CaseFactVersionResponse(
                case_fact_id=cfv.case_fact_id,
                case_fact_version_id=case_analysis_version.id,
                version_number=cfv.version_number,
                fact=cfv.fact,
            )
            for cfv in case_fact_versions
        ]

        return CaseAnalysisVersionCaster.base_to_response(
            case_analysis_version, case_facts
        )

    async def generate_analysis_answer(
        self, case_analysis_session_id: UUID, case_facts: List[str]
    ) -> str:
        logger.info(
            "Attempting to extract legal issues for case analysis with session id: %s",
            case_analysis_session_id,
        )

        # Extract legal issues from case facts
        legal_issues = await self._chatbot_service.extract_issues(case_facts)
        if not legal_issues:
            raise ChatException(
                code="LLM_SERVICE_ERROR",
                message="Cannot extract legal issues from provided case facts",
            )

        logger.info(
            "Attempting to generate legal queries for case analysis with session id: %s",
            case_analysis_session_id,
        )

        # Generate queries from legal issues
        generated_queries = await self._chatbot_service.generate_queries(legal_issues)
        if not generated_queries:
            raise ChatException(
                code="LLM_SERVICE_ERROR",
                message="Cannot generate queries for legal issues extracted",
            )

        # Vector Search
        vector_results = await self._retrieve_from_vector_search(generated_queries)
        logger.info(
            "Fetched %i chunks from vector search for sesssion with id: %s",
            len(vector_results),
            case_analysis_session_id,
        )

        # Keyword Search
        keyword_result = await self._retrieve_from_keyword_search(generated_queries)
        logger.info(
            "Fetched %i chunks from keyword search for sesssion with id: %s",
            len(keyword_result),
            case_analysis_session_id,
        )

        if not vector_results and not keyword_result:
            return ""

        deduplicated_result = self._deduplicate_results(vector_results, keyword_result)
        reranked_result = await run_in_threadpool(
            self._reranker_service.rerank, "\n".join(case_facts), deduplicated_result
        )

        logger.info(
            "Attempting to generate final answer for case analysis with session id: %s",
            case_analysis_session_id,
        )

        final_answer = await self._chatbot_service.generate_answer(
            "\n".join(case_facts), self._format_context(reranked_result[:10])
        )

        return final_answer

    def create_case_fact_version_for_update(self, updated_case_facts: dict[UUID, str]):
        case_fact_for_update = []
        for id in updated_case_facts:
            fact = updated_case_facts[id]
            if id is not None and fact is not None:
                case_fact_for_update.append(
                    CaseFactVersionCreate(
                        case_fact_id=id,
                        fact=fact,
                        is_deleted=False,
                    )
                )

        return case_fact_for_update

    def create_case_fact_version_for_deletion(self, deleted_case_facts: list[UUID]):
        case_facts_for_deletion = []
        for case_fact_id in deleted_case_facts:
            case_facts_for_deletion.append(
                CaseFactVersionUpdate(
                    id=case_fact_id,
                    is_deleted=True,
                )
            )

        return case_facts_for_deletion

    # Helpers ====================

    async def _retrieve_from_vector_search(self, queries: list[str], limit: int = 20):
        results = []
        for query in queries:
            embedding = await run_in_threadpool(
                self._embedding_service.embed_query, query
            )  # Create embeddings for query
            results.extend(
                await self._chunk_service.search_vector(
                    ChunkSearchVector(embeddings=embedding, limit=limit)
                )
            )

        return results

    async def _retrieve_from_keyword_search(self, queries: list[str], limit: int = 20):
        results = []
        for query in queries:
            results.extend(
                await self._chunk_service.search_keyword(
                    ChunkSearchKeyword(text=query, limit=limit)
                )
            )

        return results

    def _deduplicate_results(
        self, vector_results: List[Chunk], keyword_results: List[Chunk]
    ) -> list[Chunk]:
        unique_results = {}

        combined = vector_results + keyword_results
        for item in combined:
            if item.id not in unique_results:
                unique_results[item.id] = item

        return list(unique_results.values())

    def _format_context(self, results: List[Chunk]) -> str:
        formatted_results = []
        for result in results:
            document = result.document

            title = f"{document.original_file_name}.{document.file_type.lstrip('.')}"
            document_type = document.document_type.value
            chunk_text = result.chunk_text
            section = result.section if result.section else "Unknown Section"

            formatted_results.append(f"""
                Title: {title}
                Document Type: {document_type}
                Section: {section}
                
                Document: 
                {chunk_text}
                """)

        return "\n\n---\n\n".join(formatted_results)
