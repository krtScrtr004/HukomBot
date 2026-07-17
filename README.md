# Installation

### 1. Install GPU-accelerated PyTorch (requires CUDA 12.1+ compatible driver)

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### 2. Install remaining dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Setup

Copy `.env.example` to `.env` and fill in the following values:

| Variable              | Description           |
| --------------------- | --------------------- |
| `OPEN_ROUTER_API_KEY` | OpenRouter API key    |
| `NVIDIA_API_KEY`      | NVIDIA models API key |
| `HP_API_KEY`          | Hugging Face API key  |
| `DB_HOST`             | PostgreSQL host       |
| `DB_PORT`             | PostgreSQL port       |
| `DB_NAME`             | Database name         |
| `DB_USER`             | Database user         |
| `DB_PASSWORD`         | Database password     |

---

# Changelog

## Added

- Introduced a new backend API structure for document handling and case analysis workflows.
- Added new endpoints for document processing and case analysis operations.
- Implemented new database models, schemas, and repositories to support case-related data management.
- Added supporting services for embeddings, LLM integration, reranking, and file storage.

## Improved

- Refactored application architecture to use dependency-injected services for better maintainability and testability.
- Enhanced response handling through structured schema classes.
- Improved embedding and token-indexing safety with truncation handling.
- Updated project configuration, dependencies, and test setup.

## Changed

- Reorganized the application structure under the backend app package for clearer separation of concerns.
- Added new database schema and seed data files to support the expanded workflow.

## Notes

- Included temporary adjustments related to test files and workflow stability.
