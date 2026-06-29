## Installation

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

| Variable | Description |
|---|---|
| `OPEN_ROUTER_API_KEY` | OpenRouter API key |
| `HP_API_KEY` | Hugging Face API key |
| `DB_HOST` | PostgreSQL host |
| `DB_PORT` | PostgreSQL port |
| `DB_NAME` | Database name |
| `DB_USER` | Database user |
| `DB_PASSWORD` | Database password |

---

## Changelog

### Repurposed: Legal Chatbot → Case Analysis System

The system has been repurposed from a legal conversation chatbot into an AI-assisted case analysis tool.

### Migrated: ChromaDB → PostgreSQL + pgvector

#### Schema

**`documents`**

| Column | Type | Notes |
|---|---|---|
| `id` | `UUID` | Primary key |
| `title` | `TEXT` | Unique |
| `file_type` | `TEXT` | Nullable |
| `created_at` | `TIMESTAMP` | Defaults to `NOW()` |
| `search_vector` | `TSVECTOR` | Generated from `title` + `file_type` |

**`chunks`**

| Column | Type | Notes |
|---|---|---|
| `id` | `UUID` | Primary key |
| `document_id` | `UUID` | FK → `documents.id` |
| `chunk_number` | `INT` | |
| `chunk_text` | `TEXT` | |
| `embedding` | `VECTOR` | |
| `section` | `VARCHAR` | |
| `search_vector` | `TSVECTOR` | Generated from `chunk_text` + `section` |

> Deleting a `document` cascades to all its `chunks`.

### New

- **`Database` class** — connection pool management via psycopg3
- **`timer` context manager** — utility for timing individual pipeline stages
- **`RerankerService`** — reranks hybrid search results using `BAAI/bge-reranker-v2-m3`
- **`ChatbotService`** — decoupled from `LLMService`