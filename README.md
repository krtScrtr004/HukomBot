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

| Variable                    | Description                |
| --------------------------- | -------------------------- |
| `OPEN_ROUTER_API_KEY`       | OpenRouter API key         |
| `NVIDIA_API_KEY`            | NVIDIA models API key      |
| `HP_API_KEY`                | Hugging Face API key       |
| `DB_HOST`                   | PostgreSQL host            |
| `DB_PORT`                   | PostgreSQL port            |
| `DB_NAME`                   | Database name              |
| `DB_USER`                   | Database user              |
| `DB_PASSWORD`               | Database password          |
| `JWT_SECRET`                | JWT signing secret         |
| `JWT_ALGO`                  | JWT signing algorithm      |
| `JWT_ISS`                   | JWT issuer                 |
| `JWT_AUD`                   | JWT audience               |
| `JWT_EXP_IN_MIN`            | JWT expiration (mins)      |
| `OAUTH_CLIENT_ID`           | OAuth client ID            |
| `OAUTH_CLIENT_SECRET`       | OAuth client secret        |
| `GOOGLE_OAUTH_REDIRECT_URI` | Google OAuth redirect URI  |
| `GOOGLE_AUTH_URL`           | Google OAuth auth URL      |
| `GOOGLE_TOKEN_URL`          | Google OAuth token URL     |
| `OPEN_ROUTER_MODEL`         | OpenRouter model name      |
| `OPEN_ROUTER_BASE_URL`      | OpenRouter base URL        |
| `NVIDIA_MODEL`              | NVIDIA model name          |
| `NVIDIA_BASE_URL`           | NVIDIA base URL            |
| `EMBEDDING_MODEL`           | Embedding model name       |
| `EMBEDDING_DEVICE_CPU`      | Embedding CPU device label |
| `EMBEDDING_DEVICE_GPU`      | Embedding GPU device label |
| `RERANKER_MODEL`            | Reranker model name        |
| `RERANKER_DEVICE_CPU`       | Reranker CPU device label  |
| `RERANKER_DEVICE_GPU`       | Reranker GPU device label  |

---

# Changelog

## Added

- React + Vite frontend app under `frontend/hukom_bot` with TypeScript, ESLint, and path alias configuration
- Login page route and reusable UI components (`LoginCard`, `Logo`, `ProviderButton`, `ThemeToggle`)
- Sitewide theme context/provider and centered layout primitives for auth views
- Bootstrap Icons integration for UI iconography
- Backend enum `case_analysis_answer_format` and supporting caster/repository/schema files for case analysis version flow
- Reintroduced case analyses endpoint module under `backend/hukom_bot/api/v1/endpoint/case_analysis.py`

## Changes

- Rename backend package namespace from `backend.app` to `backend.hukom_bot` across API, services, repositories, schemas, and utilities
- Migrate frontend structure from legacy Python/HTML pages to a modern React component architecture
- Update theme toggle icon styling and apply theme handling globally

## Removed

- Remove legacy frontend Python templates, routers, scripts, styles, and helper modules under `frontend/`