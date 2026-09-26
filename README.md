# HukomBot

## Installation

### 1. Install GPU-Accelerated PyTorch

HukomBot uses GPU acceleration for supported ML workloads. This requires a system with a **CUDA 12.1+ compatible NVIDIA driver**.

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### 2. Install Remaining Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Configuration

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Then configure the required environment variables.

### Application

| Variable | Description |
|---|---|
| `BASE_PAGE_URL` | Frontend base URL |
| `BASE_API_URL` | Backend API base URL |

### PostgreSQL

| Variable | Description |
|---|---|
| `DB_HOST` | PostgreSQL host |
| `DB_PORT` | PostgreSQL port |
| `DB_NAME` | Database name |
| `DB_USER` | Database user |
| `DB_PASSWORD` | Database password |

### Redis

| Variable | Description |
|---|---|
| `REDIS_HOST` | Redis host |
| `REDIS_PORT` | Redis port |

### JWT

| Variable | Description |
|---|---|
| `JWT_SECRET` | JWT signing secret |
| `JWT_ALGO` | JWT signing algorithm |
| `JWT_ISS` | JWT issuer |
| `JWT_AUD` | JWT audience |
| `JWT_EXP_IN_MIN` | JWT expiration time in minutes |

### Google OAuth

| Variable | Description |
|---|---|
| `OAUTH_CLIENT_ID` | OAuth client ID |
| `OAUTH_CLIENT_SECRET` | OAuth client secret |
| `GOOGLE_OAUTH_REDIRECT_URI` | Google OAuth redirect URI |
| `GOOGLE_AUTH_URL` | Google OAuth authorization URL |
| `GOOGLE_TOKEN_URL` | Google OAuth token URL |

### LLM Providers

#### Google Gemini

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Gemini API key |
| `GEMINI_MODEL` | Gemini model name |
| `GEMINI_BASE_URL` | Gemini base URL |

#### OpenRouter

| Variable | Description |
|---|---|
| `OPEN_ROUTER_API_KEY` | OpenRouter API key |
| `OPEN_ROUTER_MODEL` | OpenRouter model name |
| `OPEN_ROUTER_BASE_URL` | OpenRouter base URL |

#### NVIDIA

| Variable | Description |
|---|---|
| `NVIDIA_API_KEY` | NVIDIA models API key |
| `NVIDIA_MODEL` | NVIDIA model name |
| `NVIDIA_BASE_URL` | NVIDIA base URL |

### Embedding and Reranking Models

| Variable | Description |
|---|---|
| `HP_API_KEY` | Hugging Face API key |
| `EMBEDDING_MODEL` | Embedding model name |
| `EMBEDDING_DEVICE_CPU` | Embedding CPU device label |
| `EMBEDDING_DEVICE_GPU` | Embedding GPU device label |
| `RERANKER_MODEL` | Reranker model name |
| `RERANKER_DEVICE_CPU` | Reranker CPU device label |
| `RERANKER_DEVICE_GPU` | Reranker GPU device label |

### Token Quota

| Variable | Description |
|---|---|
| `TOKEN_QUOTA_DAILY` | Daily token quota limit |
| `TOKEN_QUOTA_WINDOW` | Token quota window in seconds |

### Cloudinary

| Variable | Description |
|---|---|
| `CLOUDINARY_NAME` | Cloudinary cloud name |
| `CLOUDINARY_API_KEY` | Cloudinary API key |
| `CLOUDINARY_SECRET` | Cloudinary secret |

---

# API Endpoints

All API endpoints use the `/api/v1` base path.

| Method | Path | Auth | Roles | Rate Limit | Description |
|--------|------|------|-------|------------|-------------|
| `GET` | `/api/v1/auth/me` | Yes | Any | 60 req/min | Get current user profile |
| `GET` | `/api/v1/auth/google/login` | No | â€” | 10 req/min | Initiate Google OAuth |
| `GET` | `/api/v1/auth/google/login/callback` | No | â€” | 10 req/min | Handle Google OAuth callback |
| `GET` | `/api/v1/auth/logout` | Yes | Any | 20 req/min | Log out the current user |
| `GET` | `/api/v1/users/` | Yes | `admin` | 60 req/min | List/search all users |
| `GET` | `/api/v1/users/me` | Yes | Any | 60 req/min | Get current user profile |
| `GET` | `/api/v1/users/me/usage` | Yes | `standard`, `contributor` | 60 req/min | Get daily token quota usage |
| `PATCH` | `/api/v1/users/{user_id}` | Yes | Any (admin for `role` field) | 10 req/min | Update user profile |
| `DELETE` | `/api/v1/users/{id}` | Yes | `admin` | 60 req/min | Delete a user account |
| `GET` | `/api/v1/documents/` | Yes | Any | 60 req/min | List/search all documents |
| `POST` | `/api/v1/documents/` | Yes | Any | 5 req/min | Upload a document |
| `GET` | `/api/v1/documents/{id}` | Yes | Any | 60 req/min | Get document by ID |
| `PATCH` | `/api/v1/documents/{id}` | Yes | `admin` | 10 req/min | Update document metadata |
| `PATCH` | `/api/v1/documents/{id}/approve` | Yes | `admin` | 10 req/min | Approve a document |
| `GET` | `/api/v1/documents/{id}/upload-status` | Yes | Any | 60 req/min | Get document upload status |
| `DELETE` | `/api/v1/documents/{id}` | Yes | `admin` | 10 req/min | Delete a document |
| `POST` | `/api/v1/documents/bulk-delete` | Yes | `admin` | 10 req/min | Bulk delete documents |
| `GET` | `/api/v1/admin/dashboard` | Yes | `admin` | 60 req/min | Get admin dashboard data |
| `GET` | `/api/v1/admin/users` | Yes | `admin` | 60 req/min | Get admin user analytics |
| `GET` | `/api/v1/admin/documents` | Yes | `admin` | 60 req/min | Get admin document analytics |
| `GET` | `/events/v1/admin/dashboard` | Yes | `admin` | â€” | Stream admin dashboard updates (SSE) |
| `GET` | `/events/v1/admin/users` | Yes | `admin` | â€” | Stream admin user analytics updates (SSE) |
| `GET` | `/events/v1/admin/documents` | Yes | `admin` | â€” | Stream admin document analytics updates (SSE) |
| `POST` | `/api/v1/case-analyses/` | Yes | `standard`, `contributor` | 5 req/min | Run case analysis |
| `GET` | `/api/v1/case-analyses/` | Yes | `standard`, `contributor` | 60 req/min | List the user's case analysis sessions |
| `GET` | `/api/v1/case-analyses/{id}/versions` | Yes | `standard`, `contributor` | 60 req/min | List versions of a case analysis session |
| `GET` | `/api/v1/case-analyses/{id}/versions/{v}` | Yes | `standard`, `contributor` | 60 req/min | Get a specific case analysis version |
| `DELETE` | `/api/v1/case-analyses/{id}` | Yes | `standard`, `contributor` | 10 req/min | Delete a case analysis session |

---

# Token Quota

HukomBot enforces a **daily AI token quota** using Redis and a Lua script during case analysis generation.

The current user's quota usage can be retrieved through:

```http
GET /api/v1/users/me/usage
```

The response is wrapped in a `SuccessResponse` envelope:

```json
{
  "success": true,
  "data": {
    "quota": 100000,
    "remaining": 75000,
    "ttl": 3600
  }
}
```

The response fields are:

| Field | Description |
|---|---|
| `quota` | User's total daily token quota |
| `remaining` | Number of tokens remaining |
| `ttl` | Remaining lifetime of the current quota window in seconds |

---

# Image Storage

Profile pictures are stored using **Cloudinary**.

The `UserOrchistrator.update_pipeline()` method:

1. Validates the uploaded image.
2. Accepts JPG, JPEG, and PNG files.
3. Enforces a maximum file size of **5 MB**.
4. Uploads the image to Cloudinary.
5. Stores the resulting URL in the user's `profile_picture` field.
6. Removes the uploaded Cloudinary image if the database transaction fails.

This provides rollback behavior for failed profile updates, preventing orphaned uploaded images.

---

# Changelog

## Added

### Backend

- Added `created_at` and  `provider`  (`OAuthProvider`) fields to `UserResponse` schema.
- Added to `UserResponse` schema.
- Added:

  ```http
  GET /api/v1/admin/dashboard
  ```

   for retrieving admin dashboard data with aggregated counts (admin only).
- Added:

  ```http
  GET /api/v1/admin/users
  ```

   for retrieving admin user analytics with registration and role counts (admin only).
- Added:

  ```http
  GET /api/v1/admin/documents
  ```

   for retrieving admin document analytics with status, type, monthly upload counts, and top uploaders (admin only).
- Added:

  ```http
  GET /events/v1/admin/dashboard
  ```

   for streaming real-time admin dashboard updates via Server-Sent Events (SSE) (`admin` only).
- Added:

  ```http
  GET /events/v1/admin/users
  ```

   for streaming real-time user analytics updates via Server-Sent Events (SSE) (`admin` only).
- Added:

  ```http
  GET /events/v1/admin/documents
  ```

   for streaming real-time document analytics updates via Server-Sent Events (SSE) (`admin` only).
- Added `PubsubService` class wrapping Redis pub/sub for publish/subscribe messaging.
- Added `ADMIN_DASHBOARD_CH`, `ADMIN_USER_ANALYTICS_CH`, and `ADMIN_DOCUMENT_ANALYTICS_CH` configuration variables for the Redis channel names.
- Added publish (trigger) statements to document and user actions that update admin dashboard statistics.
- Added `UserSearch` schema with query-based search, filter by `is_active`, `role`, `oauth_provider`, and `OrderableMixin` for sortable columns.
- Added `UserGetAll` and `DocumentGetAll` schemas for non-search list endpoints with filter by `is_active`, `role`, `oauth_provider`.
- Added `AdminDashboardData` schema with aggregated counts for active users, documents by status, and chunks.
- Updated `AdminDashboardData` schema to include per-status, per-weekly, and per-type document counts via `DocumentStatusCount`, `DocumentWeeklyCount`, and `DocumentTypeCount` schemas.
- Updated `GET /api/v1/admin/dashboard` to accept optional `date_range`, `date_start`, and `date_end` query parameters for filtering by date range.
- Updated `GET /api/v1/admin/dashboard` to require admin authentication (previously accessible by any user).
- Updated `GET /events/v1/admin/dashboard` SSE stream to emit raw `AdminDashboardData` JSON instead of `SuccessResponse` wrapper.
- Added `date_range`, `date_start`, and `date_end` query parameters to `GET /events/v1/admin/dashboard`.
- Added `AdminUserAnalytics`, `MonthlyCount`, and `UserRoleCount` schemas for admin user analytics.
- Added `AdminDocumentAnalytics` schema for admin document analytics with status, type, monthly upload counts, and top uploaders.
- Added `uploader_id` filter to `DocumentSearch` and `DocumentGetAll` schemas.
- Added:

  ```http
  DELETE /api/v1/documents/{document_id}
  ```

   for deleting a document by ID (admin only).
- Added `DocumentService.delete()` method and corresponding repository implementation for single document deletion.
- Added:

  ```http
  POST /api/v1/documents/bulk-delete
  ```

   for bulk deletion of multiple documents by ID (admin only).
- Added `DocumentService.delete_many()` method and corresponding repository implementation for bulk document deletion.
- Changed role access for `GET /api/v1/documents/` from `admin` to `Any authenticated`.
- Changed role access for `GET /api/v1/documents/{document_id}` from `admin` to `Any authenticated`.

## Changed

### User API

The user update endpoint was restructured.

Previously:

```http
PATCH /users/me
```

with a JSON request body.

Now:

```http
PATCH /users/{user_id}
```

using `multipart/form-data` with form fields and an optional file upload.

The endpoint now uses `UserOrchistrator` for authorization and transactional updates.

**New features:**
- Added `is_active` field (admin only) - allows admins to activate/deactivate user accounts
- Profile picture can only be modified by the profile owner (not by other users or admins)
- Non-admin users cannot modify their own `is_active` status
- The endpoint uses `UserOrchistrator.update_pipeline()` for:
  - Profile updates (first_name, last_name)
  - Role changes (admin only)
  - Account activation/deactivation (admin only via `is_active`)
  - File validation and Cloudinary image uploads (profile owner only)
  - Authorization checks (self or admin; admin-only for `role` and `is_active` fields)
  - Database transactions with rollback on failure

### User Response

- Updated `UserCaster` to include `profile_picture` when converting to `UserResponse`.
- Added `role` claim to `JWTPayload` and included it in the JWT emitted at login.
- Added `require_role` dependency that validates the `role` claim against allowed roles.
- Added role guards to all case analysis endpoints, document update/approve endpoints, user token usage endpoint, document listing, and document retrieval by ID endpoints.
- Updated `rate_limit` dependency to use injected `JWTService` instead of instantiating it inline.
- `GET /users/me` success message changed from "User fetched successfully" to "User retrieved successfully".
- `GET /users/me/usage` success message changed from "User token usage retrive successfully" to "User token usage retrieved successfully".
- `UserSearch` schema restructured to use generic `query` field with `OrderableMixin` instead of separate `first_name`/`last_name`/`email`/`provider` fields.
- `DocumentSearch` schema restructured to use generic `query` field with `OrderableMixin`.
- Added `model_validator` on `DocumentUpdateBase` to enforce: `rejection_message` required when `upload_status` is `rejected`, and `upload_status` required when `rejection_message` is provided.
