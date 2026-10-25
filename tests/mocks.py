"""
Reusable mock factories for repositories and services.

These let tests isolate business logic from the real database, embedding
model, reranker, LLM, and filesystem. Each factory returns a unittest.mock
AsyncMock / MagicMock that records calls and returns safe defaults, which you
can override per-test via `return_value` / `side_effect`.

Usage:
    from tests.mocks import build_document_repository_mock, build_document_service_mock

    repo = build_document_repository_mock()
    repo.get_by_digest.return_value = None
    service = build_document_service_mock(document_repo=repo)
"""

from unittest.mock import AsyncMock, MagicMock

from uuid import uuid4


# ---------------------------------------------------------------------------
# Repository mocks
# ---------------------------------------------------------------------------


def build_chunk_repository_mock() -> MagicMock:
    repo = MagicMock()
    repo.search = AsyncMock(return_value=[])
    repo.search_vector = AsyncMock(return_value=[])
    repo.create_many = AsyncMock(return_value=[])
    return repo


def build_case_fact_repository_mock() -> MagicMock:
    repo = MagicMock()
    repo.create_many = AsyncMock(return_value=[])
    repo.delete_many = AsyncMock(return_value=None)
    return repo


def build_case_fact_version_repository_mock() -> MagicMock:
    repo = MagicMock()
    repo.create_many = AsyncMock(return_value=[])
    repo.create_updated_many = AsyncMock(return_value=[])
    repo.update_many = AsyncMock(return_value=None)
    repo.delete_many = AsyncMock(return_value=None)
    repo.get_by_version_number = AsyncMock(return_value=[])
    repo.get_latest_by_session_id = AsyncMock(return_value=[])
    return repo


def build_case_analysis_session_repository_mock() -> MagicMock:
    repo = MagicMock()
    repo.create = AsyncMock(return_value=_make_session())
    repo.is_existing_by_id = AsyncMock(return_value=True)
    return repo


def build_case_analysis_version_repository_mock() -> MagicMock:
    repo = MagicMock()
    repo.create = AsyncMock(return_value=_make_version())
    repo.get_latest_by_session_id = AsyncMock(return_value=None)
    repo.get_by_version_number = AsyncMock(return_value=None)
    return repo


def build_case_analysis_version_fact_repository_mock() -> MagicMock:
    repo = MagicMock()
    repo.create_many = AsyncMock(return_value=[])
    return repo


def build_document_repository_mock() -> MagicMock:
    repo = MagicMock()
    repo.create = AsyncMock(return_value=_make_document())
    repo.get_by_id = AsyncMock(return_value=_make_document())
    repo.get_by_digest = AsyncMock(return_value=None)
    repo.get_upload_status_by_id = AsyncMock(return_value="ONGOING")
    repo.update = AsyncMock(return_value=None)
    repo.delete_many = AsyncMock(return_value=None)
    return repo


# ---------------------------------------------------------------------------
# Service / external-dependency mocks
# ---------------------------------------------------------------------------


def build_embedding_service_mock() -> MagicMock:
    svc = MagicMock()
    svc.embed_documents = MagicMock(return_value=[[0.1, 0.2, 0.3]])
    svc.embed_query = MagicMock(return_value=[0.1, 0.2, 0.3])
    svc.max_seq_length = 512
    return svc


def build_reranker_service_mock() -> MagicMock:
    svc = MagicMock()
    svc.rerank = MagicMock(return_value=[])
    return svc


def build_llm_service_mock() -> MagicMock:
    svc = MagicMock()
    svc.chat = AsyncMock(return_value="mock llm response")
    return svc


def build_file_storage_service_mock() -> MagicMock:
    svc = MagicMock()
    svc.save_to_pending = AsyncMock(return_value=None)
    svc.get_pending_file = MagicMock(return_value=None)
    svc.delete_from_pending = AsyncMock(return_value=None)
    return svc


def build_chatbot_service_mock() -> MagicMock:
    svc = MagicMock()
    svc.extract_issues = AsyncMock(return_value=["legal issue 1"])
    svc.generate_queries = AsyncMock(return_value=["query 1"])
    svc.generate_answer = AsyncMock(return_value="final answer")
    svc.get_case_analysis_version = AsyncMock(return_value=None)
    return svc


# ---------------------------------------------------------------------------
# Assembled service mocks (handy one-liners)
# ---------------------------------------------------------------------------


def build_document_service_mock(**overrides) -> MagicMock:
    defaults = dict(
        document_repo=build_document_repository_mock(),
        chunk_repo=build_chunk_repository_mock(),
        embedding_service=build_embedding_service_mock(),
        file_storage_service=build_file_storage_service_mock(),
    )
    defaults.update(overrides)
    svc = MagicMock()
    svc.create_pending_document = AsyncMock(
        return_value=_make_pending_success()
    )
    svc.approve_document_upload = AsyncMock(
        return_value=_make_pending_success()
    )
    svc.get_upload_status = AsyncMock(return_value=_make_status_success())
    # Expose collaborators so tests can tweak behavior
    svc.document_repo = defaults["document_repo"]
    svc.chunk_repo = defaults["chunk_repo"]
    svc.embedding_service = defaults["embedding_service"]
    svc.file_storage_service = defaults["file_storage_service"]
    return svc


def build_case_analysis_service_mock(**overrides) -> MagicMock:
    defaults = dict(
        db=MagicMock(),
        chunk_repo=build_chunk_repository_mock(),
        case_fact_repo=build_case_fact_repository_mock(),
        case_fact_version_repo=build_case_fact_version_repository_mock(),
        case_analysis_session_repo=build_case_analysis_session_repository_mock(),
        case_analysis_version_repo=build_case_analysis_version_repository_mock(),
        case_analysis_version_fact_repo=(
            build_case_analysis_version_fact_repository_mock()
        ),
        chatbot_service=build_chatbot_service_mock(),
        embedding_service=build_embedding_service_mock(),
        reranker_service=build_reranker_service_mock(),
    )
    defaults.update(overrides)
    svc = MagicMock()
    svc.run_pipeline = AsyncMock(return_value=_make_post_success())
    svc.get_by_version = AsyncMock(return_value=_make_get_success())
    # Expose collaborators so tests can tweak behavior
    for key, value in defaults.items():
        setattr(svc, f"_{key}" if not key.endswith("_repo") else key, value)
    svc._db = defaults["db"]
    svc._chunk_repo = defaults["chunk_repo"]
    svc._case_fact_repo = defaults["case_fact_repo"]
    svc._case_fact_version_repo = defaults["case_fact_version_repo"]
    svc._case_analysis_session_repo = defaults["case_analysis_session_repo"]
    svc._case_analysis_version_repo = defaults["case_analysis_version_repo"]
    svc._case_analysis_version_fact_repo = (
        defaults["case_analysis_version_fact_repo"]
    )
    svc._chatbot_service = defaults["chatbot_service"]
    svc._embedding_service = defaults["embedding_service"]
    svc._reranker_service = defaults["reranker_service"]
    return svc


# ---------------------------------------------------------------------------
# Tiny response/domain stubs (avoid importing heavy schemas in simple tests)
# ---------------------------------------------------------------------------


def _make_session():
    obj = MagicMock()
    obj.id = uuid4()
    obj.created_at = "2025-01-01T00:00:00"
    obj.updated_at = "2025-01-01T00:00:00"
    return obj


def _make_version():
    obj = MagicMock()
    obj.id = uuid4()
    obj.version_number = 1
    obj.answer = "answer"
    obj.created_at = "2025-01-01T00:00:00"
    return obj


def _make_document():
    obj = MagicMock()
    obj.id = uuid4()
    obj.upload_status = "ONGOING"
    obj.file_type = ".pdf"
    obj.upload_file_name = uuid4()
    return obj


def _make_pending_success():
    obj = MagicMock()
    obj.success = True
    obj.message = "File upload is pending for approval"
    obj.data = {"document_id": str(uuid4()), "status": "PENDING"}
    return obj


def _make_status_success():
    obj = MagicMock()
    obj.success = True
    obj.message = "Document upload status is: Ongoing"
    obj.data = {"status_value": "ONGOING"}
    return obj


def _make_post_success():
    obj = MagicMock()
    obj.success = True
    obj.message = "Case analysis created successfully"
    obj.data = {
        "case_analysis_session_id": str(uuid4()),
        "case_analysis": {"id": str(uuid4()), "version_number": 1},
    }
    return obj


def _make_get_success():
    obj = MagicMock()
    obj.success = True
    obj.message = "Case analysis version fetched successfully"
    obj.data = {
        "case_analysis_session_id": str(uuid4()),
        "case_analysis": {"id": str(uuid4()), "version_number": 1},
    }
    return obj
