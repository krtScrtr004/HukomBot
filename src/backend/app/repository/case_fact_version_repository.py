from uuid import UUID
from typing import List
from psycopg import errors
from psycopg import AsyncConnection

from backend.app.database.database import Database
from backend.app.model.case_analysis_model import CaseFactVersion
from backend.app.schema.case_analysis_schema import (
    CaseFactVersionCreate,
    CaseFactVersionUpdate,
    CaseFactVersionGetBySessionId,
    CaseFactVersionGetByVersionNumber,
)


class CaseFactVersionRepository:
    def __init__(self, db: Database):
        self.__database = db

    async def create_many(
        self,
        case_fact_versions: List[CaseFactVersionCreate],
        connection: AsyncConnection = None,
    ) -> List[CaseFactVersion]:
        if not case_fact_versions:
            return []

        if connection is not None:
            return await self.__create_many_implement(connection, case_fact_versions)
        async with self.__database.connection() as conn:
            try:
                result = await self.__create_many_implement(conn, case_fact_versions)

                await conn.commit()
                return result
            except (errors.IntegrityError, errors.OperationalError) as ex:
                await conn.rollback()
                raise

    async def __create_many_implement(
        self,
        conn: AsyncConnection,
        case_fact_versions: List[CaseFactVersionCreate],
    ) -> List[CaseFactVersion]:
        async with conn.cursor() as cur:
            await cur.executemany(
                """
                INSERT INTO case_fact_versions (
                    id,
                    case_fact_id, 
                    version_number,
                    fact,
                    is_deleted,
                    created_at
                ) VALUES (
                    %(id)s,
                    %(case_fact_id)s, 
                    %(version_number)s,
                    %(fact)s,
                    %(is_deleted)s,
                    %(created_at)s
                )
                """,
                [fact_version.model_dump() for fact_version in case_fact_versions],
            )

            # Retrieve the generated IDs
            updated = []
            for i, _ in enumerate(case_fact_versions):
                updated.append(
                    CaseFactVersion(
                        id=case_fact_versions[i].id,
                        case_fact_id=case_fact_versions[i].case_fact_id,
                        version_number=case_fact_versions[i].version_number,
                        fact=case_fact_versions[i].fact,
                        is_deleted=case_fact_versions[i].is_deleted,
                        created_at=case_fact_versions[i].created_at,
                    )
                )

        return updated

    async def create_updated_many(
        self,
        case_fact_versions: List[CaseFactVersionCreate],
        connection: AsyncConnection = None,
    ) -> List[CaseFactVersion]:
        if not case_fact_versions:
            return []

        if connection is not None:
            return await self.__create__updated_many_implement(connection, case_fact_versions)
        async with self.__database.connection() as conn:
            try:
                result = await self.__create__updated_many_implement(conn, case_fact_versions)

                await conn.commit()
                return result
            except (errors.IntegrityError, errors.OperationalError) as ex:
                await conn.rollback()
                raise

    async def __create__updated_many_implement(
        self,
        conn: AsyncConnection,
        case_fact_versions: List[CaseFactVersionCreate],
    ) -> List[CaseFactVersion]:
        rows = []
        
        async with conn.cursor() as cur, conn.transaction():
            fact_ids = sorted(
                {fv.case_fact_id for fv in case_fact_versions},
                key=str,
            )
            # Lock rows for update
            await cur.execute(
                """
                SELECT id
                FROM case_facts
                WHERE id = ANY(%(case_fact_ids)s)
                ORDER BY id
                FOR UPDATE
                """,
                {"case_fact_ids": fact_ids},
            )

            for fact_version in case_fact_versions:
                await cur.execute(
                    """
                    INSERT INTO case_fact_versions (
                        id,
                        case_fact_id,
                        version_number,
                        fact,
                        is_deleted,
                        created_at
                    )
                    VALUES (
                        %(id)s,
                        %(case_fact_id)s,
                        (
                            SELECT COALESCE(MAX(version_number), 0) + 1
                            FROM case_fact_versions
                            WHERE case_fact_id = %(case_fact_id)s
                        ),
                        %(fact)s,
                        %(is_deleted)s,
                        %(created_at)s
                    )
                    RETURNING
                        id,
                        case_fact_id,
                        version_number,
                        fact,
                        is_deleted,
                        created_at
                    """,
                    fact_version.model_dump(),
                )

                rows.append(await cur.fetchone())

        return [CaseFactVersion.model_validate(row) for row in rows]

    async def update_many(
        self,
        case_facts: List[CaseFactVersionUpdate],
        connection: AsyncConnection = None,
    ):
        if not case_facts:
            return

        if connection is not None:
            await self.__update_many_implement(connection, case_facts)
        else:
            async with self.__database.connection() as conn:
                try:
                    await self.__update_many_implement(conn, case_facts)
                    await conn.commit()
                except (errors.IntegrityError, errors.OperationalError) as ex:
                    await conn.rollback()
                    raise

    async def __update_many_implement(
        self, conn: AsyncConnection, case_facts: List[CaseFactVersionUpdate]
    ):
        query, params = self.__build_update_many_query(case_facts)

        async with conn.cursor() as cur:
            await cur.execute(query, params)

    def __build_update_many_query(self, case_facts: List[CaseFactVersionUpdate]):
        values_placeholder = []
        values = {}
        for i, case_fact in enumerate(case_facts):
            d = case_fact.model_dump()
            values_placeholder.append(
                f"(%(id{i})s::uuid, %(version_number{i})s::int, %(fact{i})s::text, %(is_deleted{i})s::bool)"
            )
            values[f"id{i}"] = d["id"]
            values[f"version_number{i}"] = d["version_number"]
            values[f"fact{i}"] = d["fact"]
            values[f"is_deleted{i}"] = d["is_deleted"]

        query = f"""
            UPDATE case_fact_versions AS cfv
            SET 
                version_number = COALESCE(v.version_number, cfv.version_number),
                fact = COALESCE(v.fact, cfv.fact),
                is_deleted = COALESCE(v.is_deleted, cfv.is_deleted)
            FROM (VALUES
                {", ".join(values_placeholder)}
            ) AS v(
                id, 
                version_number,
                fact,
                is_deleted
            ) WHERE cfv.id = v.id
        """

        return query, values

    async def get_by_version_number(self, param: CaseFactVersionGetByVersionNumber):
        async with self.__database.connection() as conn:
            try:
                async with conn.cursor() as cur:                    
                    session_id_query = ""
                    if param.case_analysis_session_id:
                        session_id_query = "cav.case_analysis_session_id = %(case_analysis_session_id)s AND "
                    
                    await cur.execute(
                        f"""
                        SELECT cfv.*
                        FROM case_analysis_version_facts cavf
                        JOIN case_analysis_versions cav 
                            ON cav.id = cavf.case_analysis_version_id
                        JOIN case_fact_versions cfv
                            ON cfv.id = cavf.case_fact_version_id
                        WHERE {session_id_query}
                            cav.version_number = %(version_number)s
                            AND cfv.is_deleted = FALSE
                        ORDER BY cfv.created_at
                        LIMIT %(limit)s
                        OFFSET %(offset)s
                        """,
                        param.model_dump(),
                    )

                    row = await cur.fetchall()
                await conn.commit()
                return [CaseFactVersion.model_validate(case_fact) for case_fact in row]
            except (errors.OperationalError, errors.IntegrityConstraintViolation) as ex:
                raise
            
    async def get_latest_by_session_id(self, param: CaseFactVersionGetBySessionId):
        async with self.__database.connection() as conn:
            try:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        SELECT *
                        FROM (
                            SELECT DISTINCT ON (cf.id)
                                cfv.*
                            FROM case_facts cf
                            JOIN case_fact_versions cfv
                                ON cfv.case_fact_id = cf.id
                            WHERE cf.case_analysis_session_id = %(case_analysis_session_id)s
                            ORDER BY
                                cf.id,
                                cfv.version_number DESC
                        ) latest
                        WHERE latest.is_deleted = FALSE
                        ORDER BY latest.created_at
                        LIMIT %(limit)s
                        OFFSET %(offset)s
                        """,
                        param.model_dump(),
                    )

                    row = await cur.fetchall()
                await conn.commit()
                return [CaseFactVersion.model_validate(case_fact) for case_fact in row]
            except (errors.OperationalError, errors.IntegrityConstraintViolation) as ex:
                raise

    async def delete_many(self, ids: List[UUID], connection: AsyncConnection = None):
        if not ids:
            return

        if connection is not None:
            await self.__delete_many_implement(connection, ids)
        else:
            async with self.__database.connection() as conn:
                try:
                    await self.__delete_many_implement(conn, ids)
                    await conn.commit()
                except errors.OperationalError as ex:
                    await conn.rollback()
                    raise

    async def __delete_many_implement(self, conn: AsyncConnection, ids: List[UUID]):
        async with conn.cursor() as cur:
            placeholders = ", ".join(["%s"] * len(ids))
            await cur.execute(
                f"""
                DELETE FROM case_fact_versions
                WHERE id IN ({placeholders})
                """,
                ids,
            )
