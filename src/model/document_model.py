import uuid
from model.model import Model
from datetime import datetime
from psycopg import errors


class DocumentModel(Model):
    def __init__(
        self,
        id: uuid = None,
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

        try:
            file_type_c = self.file_type
            if not file_type_c:
                file_type_c = None
            created_at_c = self.created_at
            if not created_at_c:
                created_at_c = datetime.now

            with self.connection.conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO documents (
                        title, file_type, created_at
                    ) VALUES (
                        %s, %s, %s
                    )
                    """,
                    (self.title, file_type_c, created_at_c),
                )
            self.connection.conn.commit()
        except errors.IntegrityError as ex:
            print(f"Duplicate id exception: {ex}")
            self.connection.conn.rollback()
        except errors.OperationalError as ex:
            print(f"Insert error: {ex}")
            raise

    def search(self, title: str = "", file_type: str = None) -> list:
        if not title and not file_type:
            raise RuntimeError("Title OR file_type parameters must be provided")
        try:
            combined_terms = ""
            if title:
                combined_terms += f" {title}"
            if file_type:
                combined_terms += f" {file_type}"

            with self.connection.conn.cursor() as cur:
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
                        id=uuid.UUID(row["id"]),
                        title=row["title"],
                        file_type=row["file_type"],
                        created_at=datetime.fromisoformat(row["created_at"]),
                    )
                    documents.append(document)

                return documents
        except errors.OperationalError as ex:
            print(f"Search error: {ex}")
            raise
