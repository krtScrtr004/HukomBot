import logging
from psycopg import AsyncConnection
from backend.app.database.database import Database
from backend.app.schema.case_analysis_schema import *
from backend.app.service.case_analysis_service import CaseAnalysisService
from backend.app.schema.chatbot_schema import (
    CaseAnalysisPipelineCaseFactsPayload,
    PostCaseAnalysisResponse,
)
from backend.app.schema.orchistrator_schema import OrchistratorResult
from backend.app.util.case_analysis_version_caster import CaseAnalysisVersionCaster
from backend.app.exception.not_found_exception import NotFoundException

logger = logging.getLogger(__name__)


class CaseAnalysisOrchistrator:
    def __init__(self, db: Database, case_analysis_service: CaseAnalysisService):
        self._db = db
        self._service = case_analysis_service

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

    async def _run_fresh_pipeline(self, case_facts: list[str]):
        session = CaseAnalysisSessionCreate()

        async with self._db.connection() as conn:
            async with conn.transaction():
                try:
                    # final_answer = await self._service.generate_analysis_answer(
                    #     session.id, case_facts
                    # )
                    final_answer = "aaaaa"

                    # Create session
                    await self._service.create_session(session, conn)
                    logger.info(
                        "Created new case analysis session with id: %s", session.id
                    )

                    # Create case facts
                    case_fact_objs = await self._service.create_facts(
                        session_id=session.id, facts=case_facts, connection=conn
                    )

                    # Create case fact versions
                    case_fact_version_objs = await self._service.create_fact_versions(
                        version_number=1,
                        raw_facts=case_facts,
                        obj_facts=case_fact_objs,
                        connection=conn,
                    )

                    # Create case analysis version
                    case_analysis_version_obj = (
                        await self._service.create_analysis_version(
                            session_id=session.id,
                            version_number=1,
                            answer=final_answer,
                            connection=conn,
                        )
                    )

                    # Create case analysis fact versions
                    await self._service.create_analysis_version_fact(
                        facts_count=len(case_facts),
                        analysis_version_id=case_analysis_version_obj.id,
                        facts=case_fact_version_objs,
                        connection=conn,
                    )

                    logger.info(
                        "Responded to case analysis session id: %s successfully",
                        session.id,
                    )

                    return OrchistratorResult(
                        message="Case analysis created successfully",
                        data=PostCaseAnalysisResponse(
                            case_analysis_session_id=session.id,
                            case_analysis=CaseAnalysisVersionCaster.base_to_response(
                                case_analysis_version_obj
                            ),
                        ),
                    )
                except Exception as ex:
                    logger.exception(str(ex))
                    raise

    async def _run_existing_pipeline(
        self,
        session_id: UUID,
        new_facts: list[str] | None = None,
        updated_facts: dict[UUID, str] | None = None,
        deleted_facts: list[UUID] | None = None,
    ):
        await self._service.ensure_valid_session_id(session_id)

        # Retrieve the last anlysis version
        latest_analysis_version = (
            await self._service.get_latest_analysis_version_by_session_id(session_id)
        )
        if not latest_analysis_version:
            raise NotFoundException(
                code="CASE_ANALYSIS_VERSION_NOT_FOUND",
                message="Case analysis failed",
                details=[
                    f"Latest case analysis version for session with id: {session_id} not found"
                ],
            )
        updated_analysis_version = latest_analysis_version.version_number + 1

        # Used for performing rollback on phase 1
        [created_new_case_fact_ids, updated_case_fact_version_ids] = (
            await self._perform_phase_one(
                session_id, new_facts, updated_facts, deleted_facts
            )
        )

        case_analysis_version_obj = await self._perform_phase_two(
            session_id,
            deleted_facts,
            updated_analysis_version,
            created_new_case_fact_ids,
            updated_case_fact_version_ids,
        )

        return OrchistratorResult(
            message="Case analysis created successfully",
            data=PostCaseAnalysisResponse(
                case_analysis_session_id=session_id,
                case_analysis=CaseAnalysisVersionCaster.base_to_response(
                    case_analysis_version_obj
                ),
            ),
        )

    async def _perform_phase_one(
        self,
        session_id: UUID,
        new_facts: list[str] | None = None,
        updated_facts: dict[UUID, str] | None = None,
        deleted_facts: list[UUID] | None = None,
    ):
        created_new_case_fact_ids = []
        updated_case_fact_version_ids = []

        async with self._db.connection() as conn:
            async with conn.transaction():
                try:
                    # Create new case facts
                    if new_facts:
                        case_fact_objs = await self._service.create_facts(
                            session_id=session_id, facts=new_facts, connection=conn
                        )
                        created_new_case_fact_ids = [cf.id for cf in case_fact_objs]

                        await self._service.create_fact_versions(
                            version_number=1,
                            raw_facts=new_facts,
                            obj_facts=case_fact_objs,
                            connection=conn,
                        )

                    # Create new version for updated case facts
                    case_fact_for_update = (
                        self._service.create_case_fact_version_for_update(
                            updated_facts or []
                        )
                    )
                    if case_fact_for_update:
                        case_fact_version_objs = (
                            await self._service.create_updated_fact_versions(
                                case_fact_for_update, conn
                            )
                        )
                        updated_case_fact_version_ids = [
                            cfv.id for cfv in case_fact_version_objs
                        ]

                    # Mark case facts for deletion in the db
                    case_facts_for_deletion = (
                        self._service.create_case_fact_version_for_deletion(
                            deleted_facts or []
                        )
                    )
                    if case_facts_for_deletion:
                        await self._service.update_case_fact_versions(
                            fact_versions=case_facts_for_deletion, connection=conn
                        )

                    return (
                        created_new_case_fact_ids,
                        updated_case_fact_version_ids,
                    )
                except Exception as ex:
                    logger.error(
                        "An error occured while performing phase 1 of exisiting case analysis pipeline"
                    )

                    logger.exception(str(ex))
                    raise

    async def _perform_phase_two(
        self,
        session_id: UUID,
        deleted_facts: list[UUID],
        updated_analysis_version: int,
        created_case_fact_ids: List[UUID] = [],
        updated_case_fact_version_ids: List[UUID] = [],
    ):
        async with self._db.connection() as conn:
            try:
                latest_case_fact_objs = (
                    await self._service.get_latest_fact_version_by_session_id(
                        session_id=session_id
                    )
                )
                if not latest_case_fact_objs:
                    raise NotFoundException(
                        code="CASE_FACT_NOT_FOUND",
                        message="Case analysis failed",
                        details=[
                            f"Case facts cannot be fetched for case analysis session with id: {session_id}"
                        ],
                    )

                # Remove deleted case facts on latest case analysis so that it wont create case_analysis_version_fact entries
                if deleted_facts:
                    for cf in latest_case_fact_objs:
                        if cf.id in deleted_facts:
                            latest_case_fact_objs.remove(cf)

                # final_answer = await self._service.generate_analysis_answer(
                #     session_id,
                #     [fact.fact for fact in latest_case_fact_objs],
                # )

                final_answer = "bbbbbbbbb"

                # Create case analysis version
                case_analysis_version_obj = await self._service.create_analysis_version(
                    session_id=session_id,
                    version_number=updated_analysis_version,
                    answer=final_answer,
                    connection=conn,
                )

                await self._service.create_analysis_version_fact(
                    facts_count=len(latest_case_fact_objs),
                    analysis_version_id=case_analysis_version_obj.id,
                    facts=latest_case_fact_objs,
                    connection=conn,
                )

                await conn.commit()

                logger.info(
                    "Responded to case analysis session id: %s successfully",
                    session_id,
                )

                return case_analysis_version_obj
            except Exception as ex:
                logger.error(
                    "An error occured while performing phase 2 of exisiting case analysis pipeline"
                )

                # Rollback phase 1 db modifications
                if (
                    created_case_fact_ids
                    or updated_case_fact_version_ids
                    or deleted_facts
                ):
                    logger.error(
                        "Performing phase 1 rollback for case analysis session with id: %s",
                        session_id,
                    )

                    await self._rollback_phase_one(
                        conn,
                        created_case_fact_ids,
                        updated_case_fact_version_ids,
                        deleted_facts,
                    )

                await conn.rollback()

                logger.exception(str(ex))
                raise

    async def _rollback_phase_one(
        self,
        conn: AsyncConnection,
        created_case_fact_ids: List[UUID] = [],
        updated_case_fact_version_ids: List[UUID] = [],
        deleted_case_fact_version_ids: List[UUID] = [],
    ):
        # Rollback new case facts
        if created_case_fact_ids:
            await self._service.delete_case_facts(created_case_fact_ids, conn)

        # Rollback updated case fact versions
        if updated_case_fact_version_ids:
            await self._service.delete_case_fact_versions(
                updated_case_fact_version_ids, conn
            )

        if deleted_case_fact_version_ids:
            await self._service.update_case_fact_versions(
                [
                    CaseFactVersionUpdate(id=cfv, is_deleted=False)
                    for cfv in deleted_case_fact_version_ids
                ],
                connection=conn,
            )

        await conn.commit()
