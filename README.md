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
| `JWT_SECRET`          | JWT signing secret    |
| `JWT_ALGO`            | JWT signing algorithm |
| `JWT_ISS`             | JWT issuer            |
| `JWT_AUD`             | JWT audience          |
| `JWT_EXP_IN_MIN`      | JWT expiration (mins) |
| `OAUTH_CLIENT_ID`     | OAuth client ID       |
| `OAUTH_CLIENT_SECRET` | OAuth client secret   |
| `GOOGLE_OAUTH_REDIRECT_URI` | Google OAuth redirect URI |
| `GOOGLE_AUTH_URL`     | Google OAuth auth URL |
| `GOOGLE_TOKEN_URL`    | Google OAuth token URL |
| `OPEN_ROUTER_MODEL`   | OpenRouter model name |
| `OPEN_ROUTER_BASE_URL`| OpenRouter base URL   |
| `NVIDIA_MODEL`        | NVIDIA model name     |
| `NVIDIA_BASE_URL`     | NVIDIA base URL       |
| `EMBEDDING_MODEL`     | Embedding model name  |
| `EMBEDDING_DEVICE_CPU`| Embedding CPU device label |
| `EMBEDDING_DEVICE_GPU`| Embedding GPU device label |
| `RERANKER_MODEL`      | Reranker model name   |
| `RERANKER_DEVICE_CPU` | Reranker CPU device label |
| `RERANKER_DEVICE_GPU` | Reranker GPU device label |

---

# Changelog

## Added

- Added authentication endpoint and schemas for login and provider-based identity flows.
- Added `AuthService`, `JWTService`, `GoogleService`, and `UserService` to support request authentication and user lifecycle operations.
- Added dependency helpers to resolve and verify authenticated users on protected endpoints.
- Added request middleware to attach request identifiers and timing data to incoming HTTP requests.
- Added user role enum and OAuth-related exception handling.
- Added orchestrator layer for case analysis and document flows.
- Added caster utility classes for case analysis, case facts, user, chunk, and document type conversions.
- Added lightweight frontend login scaffolding (app, router, page, and layout templates).

## Improved

- Improved secure endpoint enforcement by verifying users before executing protected operations.
- Improved JWT verification behavior by returning decoded payload data for downstream authorization logic.
- Improved case analysis and document creation flows by propagating authenticated user context (`user_id`, `uploader_id`).
- Improved repository SQL insert scripts and model/schema mappings to persist uploader and user ownership data.
- Improved endpoint behavior by changing case analysis version retrieval from `POST` to `GET`.

## Changed

- Reorganized application modules from `src/backend/app` into top-level `backend/app` for clearer backend/frontend separation.
- Moved settings constants into environment-driven configuration.
- Split Python requirements into backend and frontend specific dependency files.
- Moved `main_cli.py` to the repository root.
- Expanded required `.env` variables to cover database, JWT, OAuth, Google OAuth, model endpoints, and embedding/reranker runtime settings.

## Notes

- Includes broad file moves and renames as part of the backend package restructuring.
- Includes minor fixes to repository lookup behavior and typo-level consistency updates.
