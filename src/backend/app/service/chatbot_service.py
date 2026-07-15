import logging

from uuid import UUID
from typing import List, Dict, Optional
from fastapi import HTTPException
from psycopg import AsyncConnection
from fastapi.concurrency import run_in_threadpool

from backend.app.database.database import Database

from backend.app.model.chunk_model import Chunk

from backend.app.schema.chunk_schema import ChunkSearchKeyword, ChunkSearchVector
from backend.app.schema.chatbot_schema import (
    CaseAnalysisPipelineCaseFactsPayload,
    GetCaseAnalysisResponse,
    ChatPipelineResponse,
)
from backend.app.schema.case_analysis_schema import (
    CaseAnalysisSessionCreate,
    CaseAnalysisVersionCreate,
    CaseFactCreate,
    CaseFactVersionCreate,
    CaseFactVersionUpdate,
    CaseFactVersionGetBySessionId,
    CaseAnalysisGetByVersionNumber,
    CaseAnalysisVersionFactCreate,
)

from backend.app.service.llm_service import LLMService
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

from backend.app.util.utility import format_conversation_history

logger = logging.getLogger(__name__)


class ChatbotService:
    def __init__(
        self,
        db: Database,
        embedding_service: EmbeddingService,
        reranker_service: RerankerService,
    ):
        self.__db = db

        self.__chunk_repo = ChunkRepository(db)
        self.__case_fact_repo = CaseFactRepository(db)
        self.__case_fact_version_repo = CaseFactVersionRepository(db)
        self.__case_analysis_session_repo = CaseAnalysisSessionRepository(db)
        self.__case_analysis_version_repo = CaseAnalysisVersionRepository(db)
        self.__case_analysis_version_fact_repo = CaseAnalysisVersionFactRepository(db)

        self.__llm_service = LLMService()
        self.__embedding_service = embedding_service
        self.__reranker_service = reranker_service

    async def get_case_analysis_version(
        self, case_analysis_session_id: UUID, version_number: int
    ):
        await self.__ensure_valid_case_analysis_session_id(case_analysis_session_id)
        
        param = CaseAnalysisGetByVersionNumber(
            case_analysis_session_id=case_analysis_session_id,
            version_number=version_number,
        )

        # Get case facts
        case_fact_versions = await self.__case_fact_version_repo.get_by_version_number(param)
        if not case_fact_versions:
            raise NotFoundException(
                f"No case fact versions found for session {case_analysis_session_id} version {version_number}",
            )
            
        case_analysis_version = await self.__case_analysis_version_repo.get_by_version_number(param)
        if not case_analysis_version:
            raise NotFoundException(
                f"No case analysis versions found for session {case_analysis_session_id} version {version_number}",
            )
            
        return GetCaseAnalysisResponse(
            case_analysis_session_id=case_analysis_session_id,
            case_analysis=[
                GetCaseAnalysisResponse.CaseAnalysisFact(
                    case_analysis=case_analysis_version,
                    case_facts=case_fact_versions
                )
            ]
        )

    async def run_case_analysis_pipeline(
        self, payload: CaseAnalysisPipelineCaseFactsPayload
    ):
        if not payload.conversation_id:
            return await self.__run_fresh_case_analysis_pipeline(payload.new_case_facts)
        else:
            return await self.__run_existing_case_analysis_pipeline(
                payload.conversation_id,
                payload.new_case_facts,
                payload.updated_case_facts,
                payload.deleted_case_facts,
            )

    async def __run_fresh_case_analysis_pipeline(self, case_facts: List[str]):
        session = CaseAnalysisSessionCreate()

        final_answer = await self.__process_case_analysis_llm_pipeline(
            session.id, case_facts
        )

        # Perform db operation
        async with self.__db.connection() as conn:
            try:
                # Create session db instance
                await self.__case_analysis_session_repo.create(session, connection=conn)
                logger.info("Created new case analysis session with id: %s", session.id)

                # Create case facts db instance
                case_fact_objs = await self.__case_fact_repo.create_many(
                    [
                        CaseFactCreate(case_analysis_session_id=session.id)
                        for _ in case_facts
                    ],
                    connection=conn,
                )

                case_fact_version_objs = await self.__case_fact_version_repo.create_many(
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
                case_analysis_version = await self.__case_analysis_version_repo.create(
                    CaseAnalysisVersionCreate(
                        case_analysis_session_id=session.id,
                        version_number=1,  # Always 1st version on fresh conversation
                        answer=final_answer,
                    ),
                    connection=conn,
                )

                await self.__case_analysis_version_fact_repo.create_many(
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
                return ChatPipelineResponse(
                    messages=["Chat responded successfully"],
                    conversation_id=session.id,
                    answer=final_answer,
                )
            except Exception as ex:
                await self.__rollback_case_analysis_pipeline(session.id, conn, ex)

    async def __run_existing_case_analysis_pipeline(
        self,
        case_analysis_session_id: UUID,
        new_case_facts: Optional[List[str]] = None,
        updated_case_facts: Optional[Dict[UUID, str]] = None,
        deleted_case_facts: Optional[List[UUID]] = None,
    ):
        await self.__ensure_valid_case_analysis_session_id(case_analysis_session_id)

        latest_analysis_version = (
            await self.__case_analysis_version_repo.get_latest_by_session_id(
                case_analysis_session_id
            )
        )
        if not latest_analysis_version:
            raise NotFoundException(
                f"Latest case analysis version for session with id: {case_analysis_session_id} not found"
            )
        updated_analysis_version = latest_analysis_version.version_number + 1

        # Used for performing rollback on phase 1
        created_new_case_fact_ids = []
        created_updated_case_fact_version_ids = []

        # PHASE 1: Perform creation / modification of case facts in the db
        async with self.__db.connection() as conn:
            try:
                # Create new case facts
                if new_case_facts:
                    # Create case facts db instance
                    case_fact_objs = await self.__case_fact_repo.create_many(
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
                    await self.__case_fact_version_repo.create_many(
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
                case_fact_for_update = self.__create_case_fact_version_for_update(
                    updated_case_facts or []
                )
                if case_fact_for_update:
                    case_fact_version_objs = (
                        await self.__case_fact_version_repo.create_updated_many(
                            case_fact_for_update,
                            connection=conn,
                        )
                    )
                    created_updated_case_fact_version_ids = [
                        cfv.id for cfv in case_fact_version_objs
                    ]

                # Mark case facts for deletion in the db
                case_facts_for_deletion = self.__create_case_fact_version_for_deletion(
                    deleted_case_facts or []
                )
                if case_facts_for_deletion:
                    await self.__case_fact_version_repo.update_many(
                        case_facts=case_facts_for_deletion, connection=conn
                    )

                await conn.commit()
            except Exception as ex:
                await self.__rollback_case_analysis_pipeline(
                    case_analysis_session_id, conn, ex
                )

        # PHASE 2: Generate answer / create analysis version
        async with self.__db.connection() as conn:
            try:
                # Get latest case analysis version
                latest_case_fact_objects = (
                    await self.__case_fact_version_repo.get_latest_by_session_id(
                        CaseFactVersionGetBySessionId(
                            case_analysis_session_id=case_analysis_session_id
                        )
                    )
                )
                if not latest_case_fact_objects:
                    raise ChatException("Case facts cannot be fetched")

                # Remove deleted case facts on latest case analysis so that it wont create case_analysis_version_fact entries
                if deleted_case_facts:
                    for cf in latest_case_fact_objects:
                        if cf.id in deleted_case_facts:
                            latest_case_fact_objects.remove(cf)

                final_answer = await self.__process_case_analysis_llm_pipeline(
                    case_analysis_session_id,
                    [fact.fact for fact in latest_case_fact_objects],
                )

                # Create analysis version db instance
                case_analysis_version_fact = (
                    await self.__case_analysis_version_repo.create(
                        CaseAnalysisVersionCreate(
                            case_analysis_session_id=case_analysis_session_id,
                            version_number=updated_analysis_version,
                            answer=final_answer,
                        ),
                        connection=conn,
                    )
                )

                await self.__case_analysis_version_fact_repo.create_many(
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

                return ChatPipelineResponse(
                    messages=["Chat responded successfully"],
                    conversation_id=case_analysis_session_id,
                    answer=final_answer,
                )
            except Exception as ex:
                # Rollback phase 1 db modifications
                if (
                    created_new_case_fact_ids
                    or created_updated_case_fact_version_ids
                    or deleted_case_facts
                ):
                    await self.__rollback_phase_one(
                        conn,
                        created_new_case_fact_ids,
                        created_updated_case_fact_version_ids,
                        deleted_case_facts,
                    )

                await self.__rollback_case_analysis_pipeline(
                    case_analysis_session_id, conn, ex
                )

    async def __process_case_analysis_llm_pipeline(
        self, case_analysis_session_id: UUID, case_facts: List[str]
    ) -> str:
        # Extract legal issues from case facts
        legal_issues = await self.extract_issues(case_facts)
        if not legal_issues:
            raise ChatException("Cannot extract legal issues from provided case facts")

        # Generate queries from legal issues
        generated_queries = await self.generate_queries(legal_issues)
        if not generated_queries:
            raise ChatException("Cannot generate queries for legal issues extracted")

        # Vector Search
        vector_results = await self.__retrieve_from_vector_search(generated_queries)
        logger.info(
            "Fetched %i chunks from vector search for sesssion with id: %s",
            len(vector_results),
            case_analysis_session_id,
        )

        # Keyword Search
        keyword_result = await self.__retrieve_from_keyword_search(generated_queries)
        logger.info(
            "Fetched %i chunks from keyword search for sesssion with id: %s",
            len(keyword_result),
            case_analysis_session_id,
        )

        # Early exit if no retrieved chunks
        if not vector_results and not keyword_result:
            return ChatPipelineResponse(
                messages=["Chat responded successfully", "No results found"],
                answer="",
            )

        deduplicated_result = self.__deduplicate_results(vector_results, keyword_result)
        reranked_result = await run_in_threadpool(
            self.__reranker_service.rerank, "\n".join(case_facts), deduplicated_result
        )

        final_answer = await self.generate_answer(
            "\n".join(case_facts), self.__format_context(reranked_result[:10])
        )

        return final_answer

    async def __retrieve_from_vector_search(self, queries: list[str], limit: int = 20):
        results = []
        for query in queries:
            embedding = await run_in_threadpool(
                self.__embedding_service.embed_query, query
            )  # Create embeddings for query
            results.extend(
                await self.__chunk_repo.search_vector(
                    ChunkSearchVector(embeddings=embedding, limit=limit)
                )
            )

        return results

    async def __retrieve_from_keyword_search(self, queries: list[str], limit: int = 20):
        results = []
        for query in queries:
            results.extend(
                await self.__chunk_repo.search(
                    ChunkSearchKeyword(text=query, limit=limit)
                )
            )

        return results

    def __deduplicate_results(
        self, vector_results: List[Chunk], keyword_results: List[Chunk]
    ) -> list[Chunk]:
        unique_results = {}

        combined = vector_results + keyword_results
        for item in combined:
            if item.id not in unique_results:
                unique_results[item.id] = item

        return list(unique_results.values())

    def __format_context(self, results: List[Chunk]) -> str:
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

    def __create_case_fact_version_for_update(
        self, updated_case_facts: Dict[UUID, str]
    ):
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

    def __create_case_fact_version_for_deletion(self, deleted_case_facts: List[UUID]):
        case_facts_for_deletion = []
        for case_fact_id in deleted_case_facts:
            case_facts_for_deletion.append(
                CaseFactVersionUpdate(
                    id=case_fact_id,
                    is_deleted=True,
                )
            )

        return case_facts_for_deletion

    async def __rollback_case_analysis_pipeline(
        self, case_analysis_session_id: UUID, conn: AsyncConnection, exc: Exception
    ):
        logger.error(
            "An error occured while running rag pipeline for case analysis with session id: %s",
            case_analysis_session_id,
        )
        await conn.rollback()

        logger.exception(str(exc))
        raise

    async def __rollback_phase_one(
        self,
        connection: AsyncConnection,
        created_case_fact_ids: List[UUID] = [],
        updated_case_fact_version_ids: List[UUID] = [],
        deleted_case_fact_version_ids: List[UUID] = [],
    ):
        # Rollback new case facts
        if created_case_fact_ids:
            await self.__case_fact_repo.delete_many(
                created_case_fact_ids, connection=connection
            )

        # Rollback updated case fact versions
        if updated_case_fact_version_ids:
            await self.__case_fact_version_repo.delete_many(
                updated_case_fact_version_ids, connection=connection
            )

        if deleted_case_fact_version_ids:
            await self.__case_fact_version_repo.update_many(
                [
                    CaseFactVersionUpdate(id=cfv, is_deleted=False)
                    for cfv in deleted_case_fact_version_ids
                ],
                connection=connection,
            )

        await connection.commit()

    async def extract_issues(self, case_facts: List[str]) -> List[str]:
        facts = "\n".join(f"- {fact}" for fact in case_facts)

        prompt = f"""
        You are an expert legal analyst specializing in Philippine law.

        Your task is to identify and extract the substantive legal issues that arise from the facts provided.

        ## CASE FACTS:

        ## {facts}

        INSTRUCTIONS:

        1. Identify each distinct substantive legal issue or question of law raised by the facts.

        2. Express each issue as a concise, standalone legal question beginning with "Whether...".

        3. Use standard Philippine legal terminology whenever appropriate.

        4. When reasonably supported by the facts, identify:

        * Causes of action;
        * Legal remedies;
        * Civil Code provisions;
        * Revised Penal Code provisions;
        * Republic Acts;
        * Legal doctrines;
        * Contractual relationships;
        * Party roles.

        5. Prefer legally precise issues over generic descriptions.

        Example:

        Avoid:

        * Whether there was a contract dispute.
        * Whether damages may be awarded.

        Prefer:

        * Whether the defendant substantially breached its contractual obligations.
        * Whether the plaintiff may rescind the contract under Article 1191 of the Civil Code.
        * Whether defective performance gives rise to liability for damages.

        6. Focus primarily on substantive legal issues, including:

        * Liability;
        * Validity of contracts;
        * Criminal responsibility;
        * Damages;
        * Ownership;
        * Employment rights;
        * Jurisdiction when central to the dispute.

        7. Do not include procedural matters unless they are essential to resolving the case.

        8. If multiple parties are involved, clearly identify the affected parties.

        9. Do not invent statutes, article numbers, or legal doctrines that are not reasonably supported by the facts.

        10. Return only the legal issues, one per line, with no numbering, bullets, labels, or additional text.

        OUTPUT FORMAT:

        Whether ...
        Whether ...
        Whether ...
        """

        response = await self.__llm_service.chat(
            prompt=prompt, temperature=0.1, max_tokens=500
        )
        if not response:
            return []

        return [line.strip() for line in response.splitlines() if line.strip()]

    async def generate_queries(
        self, legal_issues: List[str], query_count: int = 5
    ) -> List[str]:
        issues = "\n".join(f"- {issue}" for issue in legal_issues)

        prompt = f"""
        You are a legal search query generator for a Philippine law retrieval system.

        Task:
        Generate {query_count} concise, diverse, and legally precise search queries that will maximize retrieval of relevant Philippine jurisprudence, statutes, codal provisions, and legal doctrines.

        ## LEGAL ISSUES:

        ## {issues}

        REQUIREMENTS:

        1. Preserve the original legal meaning of each issue.
        2. Use standard Philippine legal terminology and doctrine.
        3. Expand issues into related legal concepts, causes of action, remedies, defenses, codal provisions, or legal principles when reasonably supported.
        4. Include specific references to:

        * Civil Code articles
        * Revised Penal Code provisions
        * Republic Act numbers
        * Rules of Court provisions
        * Legal doctrines
            whenever clearly applicable.
        5. Prefer legally meaningful search terms over plain-language descriptions.
        6. Generate queries with varied perspectives, including:

        * Legal issues
        * Causes of action
        * Remedies
        * Elements of liability
        * Applicable statutes or codal provisions
        * Party relationships or roles
        7. Keep each query under 15 words.
        8. Do not invent statutes, article numbers, or legal doctrines.
        9. Do not answer the legal issues or provide explanations.
        10. Return only the queries, one per line, with no numbering, bullets, or additional text.

        Examples:

        Issue:
        Incomplete performance of a software development contract.

        Possible queries:
        Article 1191 rescission for reciprocal obligations
        Damages for defective performance of service contracts
        Specific performance versus rescission under Civil Code
        Recovery of damages for incomplete contractual performance
        Breach of software development service agreement Philippines
        """

        response = await self.__llm_service.chat(prompt=prompt, temperature=0)
        if not response:
            return [legal_issues[0]] if legal_issues else []

        queries = [line.strip() for line in response.splitlines() if line.strip()]

        return queries if queries else legal_issues

    async def generate_answer(self, case_facts: List[str], context: str):
        retrieved_cases = "\n---\n".join(case_facts)

        prompt = f"""
        You are a legal research assistant specializing in Philippine law.

        Your task is to analyze the user's facts and the retrieved legal cases, then identify which cases may be relevant for legal research purposes.

        IMPORTANT RULES:

        1. Use ONLY the information contained in the retrieved cases.
        2. Do NOT invent or assume legal cases, citations, facts, doctrines, rulings, or legal principles that do not appear in the provided materials.
        3. If the retrieved information is insufficient to support a conclusion, explicitly state that the information is insufficient.
        4. Base relevance on factual similarities and legal issues, not merely because the cases involve the same statute, offense, or legal provision.
        5. Clearly distinguish:
        * Facts provided by the user;
        * Facts found in the retrieved cases; and
        * Assumptions, uncertainties, or missing information.
        6. Do NOT provide definitive legal advice, predict case outcomes, or determine liability.
        7. Present findings objectively and professionally.
        8. Do NOT merely restate the elements of a crime or legal provision unless those elements are explicitly discussed in the retrieved case.
        9. Every doctrine, ruling, or factual assertion must be supported by the retrieved context.
        10. If none of the retrieved cases have meaningful factual or legal similarities to the user's facts, do not include them under "Relevant Cases."
        11. If a case appears only marginally related, explain why the connection is weak and assign an appropriate confidence level.

        ## USER FACTS:

        ## {retrieved_cases}

        ## RETRIEVED LEGAL CASES:

        ## {context}

        Generate your response using the following format:

        ## Relevant Cases

        For each relevant case:

        ### [Case Name]

        **Facts from the Retrieved Case:**

        * Summarize only the facts that appear in the retrieved materials.
        * Do not add facts that are not explicitly provided.

        **Why it may be relevant:**

        * Identify specific factual similarities between the user's situation and the retrieved case.
        * Explain the legal issue addressed by the court.
        * Explain important factual or legal distinctions.
        * If factual similarities cannot be established from the retrieved materials, explicitly state that.

        **Key doctrine or ruling:**

        * Summarize the doctrine or ruling strictly based on the retrieved context.
        * If the retrieved information does not contain a doctrine or ruling, state:
        "The retrieved materials do not provide sufficient information regarding the court's doctrine or ruling."

        **Confidence:**

        * High: Strong factual and legal similarities supported by the retrieved materials.
        * Medium: Some similarities exist, but important distinctions or uncertainties remain.
        * Low: The connection is primarily based on a general legal topic or statute rather than closely related facts.
        
        ---

        ## Overall Analysis

        Provide a concise analysis that includes:

        ### Possible Legal Issues

        * Identify the possible legal issues suggested by the user's facts.
        * Clearly indicate when an issue is inferred rather than explicitly established.

        ### Common Themes Among Retrieved Cases

        * Describe recurring factual patterns, legal questions, or doctrines found in the retrieved cases.
        * Do not generalize beyond the provided materials.

        ### Limitations

        * Identify missing information in either the user's facts or the retrieved cases.
        * Explain any limitations that affect the reliability or completeness of the analysis.

        ---

        ## Disclaimer

        This analysis is intended solely for legal research and informational purposes. It is based only on the retrieved materials provided and does not constitute legal advice or a substitute for consultation with a qualified legal professional.
        """

        response = await self.__llm_service.chat(
            temperature=0,
            prompt=prompt,
        )

        if not response:
            raise RuntimeError("LLM service failed to generate the final answer")

        return response

    async def contextualize_query(
        self, query: str, conversation_history: List[dict[str, str]]
    ):
        prompt = f"""
        You are a query contextualization assistant for a Philippine legal retrieval system.

        Your task is to convert the user's latest question into a complete, standalone search query suitable for retrieving relevant legal documents.

        Requirements:

        * Preserve the user's intent.
        * Resolve all references using the conversation history.
        * Include the names of relevant laws, Republic Acts, codes, articles, sections, agencies, or legal concepts when available.
        * Use terminology likely to appear in legal documents.
        * Do not answer the question.
        * Do not explain your reasoning.
        * Return only the rewritten search query.
        * If the question already stands alone, return it unchanged.

        Conversation History:
        {format_conversation_history(conversation_history)}

        Latest User Question:
        {query}

        Standalone Search Query:
        """

        response = await self.__llm_service.chat(
            temperature=0,
            prompt=prompt,
        )
        if not response:
            return query  # Just return original query if LLM fails

        return response

    async def expand_query(self, query: str) -> List[str] | None:
        prompt = f"""
        Generate 5 alternative legal search queries for the following question.

        Requirements:
        - Preserve the original meaning.
        - Use legal terminology when appropriate.
        - Keep each query concise.
        - Return only the queries, one per line.

        Question:
        {query}
        """

        response = await self.__llm_service.chat(
            temperature=0,
            prompt=prompt,
        )
        if not response:
            return [query]

        generated_queries = [
            line.strip() for line in response.splitlines() if line.strip()
        ]

        return [query, *generated_queries]


    async def __ensure_valid_case_analysis_session_id(self, case_analysis_session_id: UUID):
        is_session_existing = await self.__case_analysis_session_repo.is_existing_by_id(
            case_analysis_session_id
        )
        if not is_session_existing:
            raise NotFoundException(
                f"Case analysis session with id: {case_analysis_session_id} not found"
            )
            