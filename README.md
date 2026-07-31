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

- Add `GET api/v1/auth/me` & `GET api/v1/user/me` - retrieves authenticated user information
- Add `DELETE api/v1/case-analyses/<id>` - removes a case analysis session record

## Changes

- Rename `api/v1/case-analysis` endpoint to `api/v1/case-analyses`