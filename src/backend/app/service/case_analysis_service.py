import logging
from uuid import UUID
from psycopg import AsyncConnection
from typing import List, Dict, Optional
from fastapi.concurrency import run_in_threadpool

from backend.app.database.database import Database

from backend.app.model.chunk_model import Chunk

from backend.app.schema.chunk_schema import ChunkSearchKeyword, ChunkSearchVector
from backend.app.schema.chatbot_schema import (
    CaseAnalysisPipelineCaseFactsPayload,
    GetCaseAnalysisResponse,
    PostCaseAnalysisResponse,
)
from backend.app.schema.case_analysis_schema import (
    CaseAnalysisSessionCreate,
    CaseAnalysisVersionCreate,
    CaseFactCreate,
    CaseFactVersionCreate,
    CaseFactVersionUpdate,
    CaseFactVersionGetBySessionId,
    CaseFactVersionResponse,
    CaseAnalysisGetByVersionNumber,
    CaseAnalysisVersionFactCreate,
    CaseAnalysisVersionResponse,
)
from backend.app.schema.response_schema import SuccessResponse

from backend.app.service.chatbot_service import ChatbotService
from backend.app.service.embedding_service import EmbeddingService
from backend.app.service.reranker_service import RerankerService

from backend.app.repository.chunk_repository import ChunkRepository
from backend.app.repository.case_fact_repository import CaseFactRepository
from backend.app.repository.case_fact_version_repository import (
    CaseFactVersionRepository,
)
from backend.app.repository.case_analysis_session_repository import (
    CaseAnalysisSessionRepository,
)
from backend.app.repository.case_analysis_version_repository import (
    CaseAnalysisVersionRepository,
)
from backend.app.repository.case_analysis_version_fact_repository import (
    CaseAnalysisVersionFactRepository,
)

from backend.app.exception.chat_exception import ChatException
from backend.app.exception.not_found_exception import NotFoundException

logger = logging.getLogger(__name__)


class CaseAnalysisService:
    def __init__(
        self,
        db: Database,
        embedding_service: EmbeddingService,
        reranker_service: RerankerService,
    ):
        self._db = db

        self._chunk_repo = ChunkRepository(db)
        self._case_fact_repo = CaseFactRepository(db)
        self._case_fact_version_repo = CaseFactVersionRepository(db)
        self._case_analysis_session_repo = CaseAnalysisSessionRepository(db)
        self._case_analysis_version_repo = CaseAnalysisVersionRepository(db)
        self._case_analysis_version_fact_repo = CaseAnalysisVersionFactRepository(db)

        self._chatbot_service = ChatbotService(db)
        self._embedding_service = embedding_service
        self._reranker_service = reranker_service

    async def get_by_version(self, case_analysis_session_id: UUID, version_number: int):
        await self._ensure_valid_session_id(case_analysis_session_id)

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

        return SuccessResponse(
            success=True,
            message="Case analysis version fetched successfully",
            data=GetCaseAnalysisResponse(
                case_analysis_session_id=case_analysis_session_id,
                case_analysis=CaseAnalysisVersionResponse(
                    id=case_analysis_version.id,
                    version_number=version_number,
                    answer=case_analysis_version.answer,
                    created_at=case_analysis_version.created_at,
                    case_facts=[
                        CaseFactVersionResponse(
                            case_fact_id=cfv.case_fact_id,
                            case_fact_version_id=case_analysis_version.id,
                            version_number=cfv.version_number,
                            fact=cfv.fact,
                        )
                        for cfv in case_fact_versions
                    ],
                ),
            ),
        )

    async def run_pipeline(self, payload: CaseAnalysisPipelineCaseFactsPayload):
        if not payload.case_analysis_session_id:
            return await self._run_fresh_pipeline(payload.new_case_facts)
        else:
            return await self._run_existing_pipeline(
                payload.case_analysis_session_id,
                payload.new_case_facts,
                payload.updated_case_facts,
                payload.deleted_case_facts,
            )

    async def _run_fresh_pipeline(self, case_facts: List[str]):
        session = CaseAnalysisSessionCreate()

        final_answer = await self._process_llm_pipeline(session.id, case_facts)

        # Perform db operation
        async with self._db.connection() as conn:
            try:
                # Create session db instance
                await self._case_analysis_session_repo.create(session, connection=conn)
                logger.info("Created new case analysis session with id: %s", session.id)

                # Create case facts db instance
                case_fact_objs = await self._case_fact_repo.create_many(
                    [
                        CaseFactCreate(case_analysis_session_id=session.id)
                        for _ in case_facts
                    ],
                    connection=conn,
                )

                case_fact_version_objs = await self._case_fact_version_repo.create_many(
                    [
                        CaseFactVersionCreate(
                            case_fact_id=fact.id,
                            version_number=1,  # Always 1st version on fresh conversation
                            fact=case_facts[i],
                            is_deleted=False,
                        )
                        for i, fact in enumerate(case_fact_objs)
                    ],
                    connection=conn,
                )

                # Create analysis version db instance
                case_analysis_version = await self._case_analysis_version_repo.create(
                    CaseAnalysisVersionCreate(
                        case_analysis_session_id=session.id,
                        version_number=1,  # Always 1st version on fresh conversation
                        answer=final_answer,
                    ),
                    connection=conn,
                )

                await self._case_analysis_version_fact_repo.create_many(
                    [
                        CaseAnalysisVersionFactCreate(
                            case_analysis_version_id=case_analysis_version.id,
                            case_fact_version_id=case_fact_version_objs[i].id,
                        )
                        for i, _ in enumerate(case_facts)
                    ],
                    connection=conn,
                )

                await conn.commit()

                logger.info(
                    "Responded to case analysis session id: %s successfully", session.id
                )
                return SuccessResponse(
                    success=True,
                    message="Case analysis created successfully",
                    data=PostCaseAnalysisResponse(
                        case_analysis_session_id=session.id,
                        case_analysis=CaseAnalysisVersionResponse(
                            id=case_analysis_version.id,
                            version_number=case_analysis_version.version_number,
                            answer=case_analysis_version.answer,
                            created_at=case_analysis_version.created_at,
                            case_facts=[],
                        ),
                    ),
                )
            except Exception as ex:
                await self._rollback_pipeline(session.id, conn, ex)

    async def _run_existing_pipeline(
        self,
        case_analysis_session_id: UUID,
        new_case_facts: Optional[List[str]] = None,
        updated_case_facts: Optional[Dict[UUID, str]] = None,
        deleted_case_facts: Optional[List[UUID]] = None,
    ):
        await self._ensure_valid_session_id(case_analysis_session_id)

        latest_analysis_version = (
            await self._case_analysis_version_repo.get_latest_by_session_id(
                case_analysis_session_id
            )
        )
        if not latest_analysis_version:
            raise NotFoundException(
                code="CASE_ANALYSIS_VERSION_NOT_FOUND",
                message="Case analysis failed",
                details=[
                    f"Latest case analysis version for session with id: {case_analysis_session_id} not found"
                ],
            )
        updated_analysis_version = latest_analysis_version.version_number + 1

        # Used for performing rollback on phase 1
        created_new_case_fact_ids = []
        created_updated_case_fact_version_ids = []

        # PHASE 1: Perform creation / modification of case facts in the db
        async with self._db.connection() as conn:
            try:
                # Create new case facts
                if new_case_facts:
                    # Create case facts db instance
                    case_fact_objs = await self._case_fact_repo.create_many(
                        [
                            CaseFactCreate(
                                case_analysis_session_id=case_analysis_session_id
                            )
                            for _ in new_case_facts
                        ],
                        connection=conn,
                    )
                    created_new_case_fact_ids = [cf.id for cf in case_fact_objs]

                    # Create case fact version for new case facts
                    await self._case_fact_version_repo.create_many(
                        [
                            CaseFactVersionCreate(
                                case_fact_id=fact.id,
                                version_number=1,
                                fact=new_case_facts[i],
                                is_deleted=False,
                            )
                            for i, fact in enumerate(case_fact_objs)
                        ],
                        connection=conn,
                    )

                # Create new version for updated case facts
                case_fact_for_update = self._create_case_fact_version_for_update(
                    updated_case_facts or []
                )
                if case_fact_for_update:
                    case_fact_version_objs = (
                        await self._case_fact_version_repo.create_updated_many(
                            case_fact_for_update,
                            connection=conn,
                        )
                    )
                    created_updated_case_fact_version_ids = [
                        cfv.id for cfv in case_fact_version_objs
                    ]

                # Mark case facts for deletion in the db
                case_facts_for_deletion = self._create_case_fact_version_for_deletion(
                    deleted_case_facts or []
                )
                if case_facts_for_deletion:
                    await self._case_fact_version_repo.update_many(
                        case_facts=case_facts_for_deletion, connection=conn
                    )

                await conn.commit()
            except Exception as ex:
                await self._rollback_pipeline(case_analysis_session_id, conn, ex)

        # PHASE 2: Generate answer / create analysis version
        async with self._db.connection() as conn:
            try:
                # Get latest case analysis version
                latest_case_fact_objects = (
                    await self._case_fact_version_repo.get_latest_by_session_id(
                        CaseFactVersionGetBySessionId(
                            case_analysis_session_id=case_analysis_session_id
                        )
                    )
                )
                if not latest_case_fact_objects:
                    raise NotFoundException(
                        code="CASE_FACT_NOT_FOUND",
                        message="Case analysis failed",
                        details=[
                            f"Case facts cannot be fetched for case analysis session with id: {case_analysis_session_id}"
                        ],
                    )

                # Remove deleted case facts on latest case analysis so that it wont create case_analysis_version_fact entries
                if deleted_case_facts:
                    for cf in latest_case_fact_objects:
                        if cf.id in deleted_case_facts:
                            latest_case_fact_objects.remove(cf)

                final_answer = await self._process_llm_pipeline(
                    case_analysis_session_id,
                    [fact.fact for fact in latest_case_fact_objects],
                )

                # Create analysis version db instance
                case_analysis_version_fact = (
                    await self._case_analysis_version_repo.create(
                        CaseAnalysisVersionCreate(
                            case_analysis_session_id=case_analysis_session_id,
                            version_number=updated_analysis_version,
                            answer=final_answer,
                        ),
                        connection=conn,
                    )
                )

                await self._case_analysis_version_fact_repo.create_many(
                    [
                        CaseAnalysisVersionFactCreate(
                            case_analysis_version_id=case_analysis_version_fact.id,
                            case_fact_version_id=latest_case_fact_objects[i].id,
                        )
                        for i, _ in enumerate(latest_case_fact_objects)
                    ],
                    connection=conn,
                )

                await conn.commit()

                logger.info(
                    "Responded to case analysis session id: %s successfully",
                    case_analysis_session_id,
                )

                return SuccessResponse(
                    success=True,
                    message=f"New case analysis version created successfully",
                    data=PostCaseAnalysisResponse(
                        case_analysis_session_id=case_analysis_session_id,
                        case_analysis=CaseAnalysisVersionResponse(
                            id=case_analysis_version_fact.id,
                            version_number=case_analysis_version_fact.version_number,
                            answer=case_analysis_version_fact.answer,
                            created_at=case_analysis_version_fact.created_at,
                            case_facts=[],
                        ),
                    ),
                )
            except Exception as ex:
                # Rollback phase 1 db modifications
                if (
                    created_new_case_fact_ids
                    or created_updated_case_fact_version_ids
                    or deleted_case_facts
                ):
                    logger.error(
                        "Performing phase 1 rollback for case analysis session with id: %s",
                        case_analysis_session_id,
                    )
                    await self._rollback_phase_one(
                        conn,
                        created_new_case_fact_ids,
                        created_updated_case_fact_version_ids,
                        deleted_case_facts,
                    )

                await self._rollback_pipeline(case_analysis_session_id, conn, ex)

    async def _process_llm_pipeline(
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

    async def _retrieve_from_vector_search(self, queries: list[str], limit: int = 20):
        results = []
        for query in queries:
            embedding = await run_in_threadpool(
                self._embedding_service.embed_query, query
            )  # Create embeddings for query
            results.extend(
                await self._chunk_repo.search_vector(
                    ChunkSearchVector(embeddings=embedding, limit=limit)
                )
            )

        return results

    async def _retrieve_from_keyword_search(self, queries: list[str], limit: int = 20):
        results = []
        for query in queries:
            results.extend(
                await self._chunk_repo.search(
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

    def _create_case_fact_version_for_update(self, updated_case_facts: Dict[UUID, str]):
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

    def _create_case_fact_version_for_deletion(self, deleted_case_facts: List[UUID]):
        case_facts_for_deletion = []
        for case_fact_id in deleted_case_facts:
            case_facts_for_deletion.append(
                CaseFactVersionUpdate(
                    id=case_fact_id,
                    is_deleted=True,
                )
            )

        return case_facts_for_deletion

    async def _rollback_pipeline(
        self, case_analysis_session_id: UUID, conn: AsyncConnection, exc: Exception
    ):
        logger.error(
            "An error occured while running rag pipeline for case analysis with session id: %s",
            case_analysis_session_id,
        )
        await conn.rollback()

        logger.exception(str(exc))
        raise

    async def _rollback_phase_one(
        self,
        connection: AsyncConnection,
        created_case_fact_ids: List[UUID] = [],
        updated_case_fact_version_ids: List[UUID] = [],
        deleted_case_fact_version_ids: List[UUID] = [],
    ):
        # Rollback new case facts
        if created_case_fact_ids:
            await self._case_fact_repo.delete_many(
                created_case_fact_ids, connection=connection
            )

        # Rollback updated case fact versions
        if updated_case_fact_version_ids:
            await self._case_fact_version_repo.delete_many(
                updated_case_fact_version_ids, connection=connection
            )

        if deleted_case_fact_version_ids:
            await self._case_fact_version_repo.update_many(
                [
                    CaseFactVersionUpdate(id=cfv, is_deleted=False)
                    for cfv in deleted_case_fact_version_ids
                ],
                connection=connection,
            )

        await connection.commit()

    async def _ensure_valid_session_id(self, case_analysis_session_id: UUID):
        is_session_existing = await self._case_analysis_session_repo.is_existing_by_id(
            case_analysis_session_id
        )
        if not is_session_existing:
            raise NotFoundException(
                code="CASE_ANALYSIS_NOT_FOUND", message="Case analysis not found"
            )
