from __future__ import annotations
from uuid import UUID
from typing import List, Dict, Optional
from model.model import Model
from datetime import datetime
from psycopg import errors


class DocumentModel(Model):
    def __init__(
        self,
        id: UUID = None,
        title: str = None,
        file_type: str | None = None,
        created_at: datetime | None = None,
    ):
        super().__init__()

        self.id = id
        self.title = title
        self.file_type = file_type
        self.created_at = created_at

    def create(self):
        if not self.title:
            raise RuntimeError("Title not provided")

        with self.connection.connection() as conn:
            try:
                file_type_c = self.file_type if self.file_type else None
                created_at_c = self.created_at if self.created_at else datetime.now()

                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO documents (
                            title, file_type, created_at
                        ) VALUES (
                            %s, %s, %s
                        ) RETURNING id
                        """,
                        (self.title, file_type_c, created_at_c),
                    )

                    # Set document id
                    self.id = cur.fetchone()[0]

                conn.commit()
            except errors.IntegrityError as ex:
                print(f"Integrity error exception: {ex}")
                conn.rollback()
            except errors.OperationalError as ex:
                print(f"Insert error: {ex}")
                raise

    def search(self, title: str = "", file_type: str = None) -> list:
        if not title and not file_type:
            raise RuntimeError("Title OR file_type parameters must be provided")

        with self.connection.connection() as conn:
            try:
                combined_terms = ""
                if title:
                    combined_terms += f" {title}"
                if file_type:
                    combined_terms += f" {file_type}"

                with conn.cursor() as cur:
                    cur.execute(
                        """
                        WITH query AS (
                            SELECT plainto_tsquery('english', %s) AS q
                        )
                        SELECT
                            d.*,
                            ts_rank(d.search_vector, q.q) AS rank
                        FROM documents d, query q
                        WHERE d.search_vector @@ q.q
                        ORDER BY rank DESC
                        """,
                        (combined_terms,),
                    )

                    rows = cur.fetchall()

                    documents = []
                    for row in rows:
                        document = DocumentModel(
                            id=row["id"],
                            title=row["title"],
                            file_type=row["file_type"],
                            created_at=datetime.fromisoformat(row["created_at"]),
                        )
                        documents.append(document)

                    return documents
            except errors.OperationalError as ex:
                print(f"Search error: {ex}")
                raise

    @staticmethod
    def create_many(documents: List[DocumentModel]):
        # Return if list is empty
        if not documents:
            return

        model = DocumentModel()

        params = []
        for doc in documents:
            entry = {}
            if not doc.title:
                raise RuntimeError("Title not provided")
            entry["title"] = doc.title
            # Set default to None or current time if not provided
            entry["file_type"] = doc.file_type if doc.file_type else None
            entry["created_at"] = doc.created_at if doc.created_at else datetime.now()
            params.append(entry)

        with model.connection.connection() as conn:
            try:
                with conn.cursor() as cur:
                    cur.executemany(
                        """
                        INSERT INTO documents (
                            title, file_type, created_at
                        ) VALUES (
                            %s, %s, %s
                        ) RETURNING id
                        """,
                        [
                            (param["title"], param["file_type"], param["created_at"])
                            for param in params
                        ],
                        returning=True,
                    )
                    # Retrieve the generated IDs
                    counter = 0
                    while True:
                        row = cur.fetchone()
                        if row:
                            # Update the document's ID attribute
                            documents[counter].id = row[0]
                            counter += 1
                        if not cur.nextset():
                            break

                conn.commit()
            except errors.IntegrityError as ex:
                print(f"Integrity error exception: {ex}")
                conn.rollback()
            except errors.OperationalError as ex:
                print(f"Insert error: {ex}")
                raise

    @staticmethod
    def delete_many(ids: list[UUID]):
        if not ids:
            return

        model = DocumentModel()

        with model.connection.connection() as conn:
            try:
                with conn.cursor() as cur:
                    placeholders = ", ".join(["%s"] * len(ids))
                    with conn.cursor() as cur:
                        cur.execute(
                            f"""
                            DELETE FROM documents
                            WHERE id IN ({placeholders})
                            """,
                            ids,
                        )

                conn.commit()
            except errors.IntegrityError as ex:
                print(f"Integrity error exception: {ex}")
                conn.rollback()
            except errors.OperationalError as ex:
                print(f"Insert error: {ex}")
                raise
