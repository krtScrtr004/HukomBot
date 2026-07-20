import jwt
import logging
import openai

from pydantic import ValidationError
from psycopg import errors
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

from backend.app.api.v1.endpoint.auth import auth_api_router
from backend.app.api.v1.endpoint.case_analysis import case_analysis_api_router
from backend.app.api.v1.endpoint.document import document_api_router

from frontend.router.login import login_page_router

from backend.app.schema.response_schema import ErrorResponse, ErrorPayload, ErrorDetail

from backend.app.exception.chat_exception import ChatException
from backend.app.exception.chunk_exception import ChunkFileException
from backend.app.exception.document_exception import InvalidDocumentTypeException
from backend.app.exception.not_found_exception import NotFoundException
from backend.app.exception.oauth_exception import OAuthException, GoogleEmailNotVerifiedException

from backend.app.api.v1.dependency import lifespan
from backend.app.core.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(lifespan=lifespan)

# Routers ============================================================

# APIs

app.include_router(
    router=auth_api_router,
    prefix="/api/v1/auth",
    tags=["Authentication API"],
)

app.include_router(
    router=case_analysis_api_router,
    prefix="/api/v1/case-analysis",
    tags=["Case Analysis API"],
)

app.include_router(
    router=document_api_router, prefix="/api/v1/documents", tags=["Documents API"]
)

# Pages

app.include_router(router=login_page_router, prefix="/login")

# Helper DB/Custom Mappers ============================================


async def handle_database_exception(request: Request, exc: Exception):
    logger.exception("Database error occurred: %s", str(exc))

    response_payload = ErrorResponse(
        error=ErrorPayload(
            code="DATABASE_ERROR",
            message="A database error occurred while processing your request.",
            details=[ErrorDetail(issue=str(exc))],
        )
    )
    return JSONResponse(
        status_code=500,
        content=response_payload.model_dump(),
    )


async def handle_custom_exception(request: Request, exc: Exception):
    logger.exception(getattr(exc, "message", str(exc)))

    # Fallbacks in case code or status_code are omitted on custom classes
    code = getattr(exc, "code", "APPLICATION_ERROR")
    status_code = getattr(exc, "status_code", 400)
    message = getattr(exc, "message", "An application rule was violated.")

    error_details = [ErrorDetail(issue=iss) for iss in getattr(exc, "details", [])]

    response_payload = ErrorResponse(
        error=ErrorPayload(code=code, message=message, details=error_details)
    )
    return JSONResponse(
        status_code=status_code,
        content=response_payload.model_dump(),
    )


# Exception Handlers ===================================================


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled runtime error caught: %s", str(exc))

    response_payload = ErrorResponse(
        error=ErrorPayload(
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected system error occurred.",
            details=[],
        )
    )
    return JSONResponse(
        status_code=500,
        content=response_payload.model_dump(),
    )


@app.exception_handler(HTTPException)
async def fastapi_http_exception_handler(request: Request, exc: HTTPException):
    logger.exception("FastAPI HTTP exception: %s", exc.detail)

    response_payload = ErrorResponse(
        error=ErrorPayload(code="HTTP_ERROR", message=str(exc.detail), details=[])
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=response_payload.model_dump(),
    )


@app.exception_handler(ValueError)
async def value_error_exception_handler(request: Request, exc: ValueError):
    logger.exception("ValueError encountered: %s", str(exc))

    response_payload = ErrorResponse(
        error=ErrorPayload(
            code="VALUE_ERROR",
            message="The system rejected the processed values.",
            details=[ErrorDetail(issue=str(exc))],
        )
    )
    return JSONResponse(
        status_code=422,
        content=response_payload.model_dump(),
    )
    

# JWT Exception Handlers

@app.exception_handler(jwt.ExpiredSignatureError)
async def jwt_expired_exception_handler(request: Request, exc: jwt.ExpiredSignatureError):
    logger.warning("User attempted authentication with an expired JWT token.")
    
    response_payload = ErrorResponse(
        error=ErrorPayload(
            code="TOKEN_EXPIRED",
            message="Your session has expired. Please log in again.",
            details=[]
        )
    )
    return JSONResponse(
        status_code=401,
        content=response_payload.model_dump(),
    )


@app.exception_handler(jwt.InvalidTokenError)
async def jwt_invalid_exception_handler(request: Request, exc: jwt.InvalidTokenError):
    logger.warning(f"Invalid JWT authentication attempt: {str(exc)}")
    
    response_payload = ErrorResponse(
        error=ErrorPayload(
            code="INVALID_TOKEN",
            message="The authentication token provided is malformed or invalid.",
            details=[]
        )
    )
    return JSONResponse(
        status_code=401,
        content=response_payload.model_dump(),
    )


# OpenAI Exception Handlers ============================================


@app.exception_handler(openai.RateLimitError)
async def rate_limit_exception_handler(request: Request, exc: openai.RateLimitError):
    logger.warning(f"OpenAI Rate Limit hit: {exc.message}")

    response_payload = ErrorResponse(
        error=ErrorPayload(
            code="AI_RATE_LIMIT_EXCEEDED",
            message="Rate limit exceeded. Please try your request again shortly.",
            details=[],
        )
    )
    return JSONResponse(
        status_code=429,
        content=response_payload.model_dump(),
    )


@app.exception_handler(openai.AuthenticationError)
@app.exception_handler(openai.PermissionDeniedError)
async def auth_exception_handler(request: Request, exc: openai.APIError):
    logger.error(f"OpenAI Authentication/Permission Error: {exc.message}")

    response_payload = ErrorResponse(
        error=ErrorPayload(
            code="AI_AUTHENTICATION_FAILED",
            message="Authentication with the core language model provider failed.",
            details=[],
        )
    )
    return JSONResponse(
        status_code=401,
        content=response_payload.model_dump(),
    )


@app.exception_handler(openai.BadRequestError)
@app.exception_handler(openai.NotFoundError)
async def bad_request_exception_handler(request: Request, exc: openai.APIError):
    logger.warning(f"OpenAI Client Error: {exc.message}")

    response_payload = ErrorResponse(
        error=ErrorPayload(
            code="AI_INVALID_REQUEST",
            message=f"Invalid prompt or interface parameters sent: {exc.message}",
            details=[],
        )
    )
    return JSONResponse(
        status_code=400,
        content=response_payload.model_dump(),
    )


@app.exception_handler(openai.APIConnectionError)
@app.exception_handler(openai.APITimeoutError)
async def connection_exception_handler(request: Request, exc: openai.OpenAIError):
    logger.exception("Failed to establish connection to OpenAI/NVIDIA servers.")

    response_payload = ErrorResponse(
        error=ErrorPayload(
            code="AI_SERVICE_UNAVAILABLE",
            message="The AI engine infrastructure is currently unreachable or timed out.",
            details=[],
        )
    )
    return JSONResponse(
        status_code=503,
        content=response_payload.model_dump(),
    )


@app.exception_handler(openai.OpenAIError)
async def generic_openai_exception_handler(request: Request, exc: openai.OpenAIError):
    logger.exception(f"Unhandled OpenAI SDK error occurred: {str(exc)}")

    response_payload = ErrorResponse(
        error=ErrorPayload(
            code="AI_GENERIC_SDK_ERROR",
            message="An internal engine abnormality occurred during model inference generation.",
            details=[ErrorDetail(issue=str(exc))],
        )
    )
    return JSONResponse(
        status_code=500,
        content=response_payload.model_dump(),
    )


# Schema Validation Handler ============================================


@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    logger.warning(f"Schema validation failed: {exc.json()}")

    # Format each validation error into our precise ErrorDetail objects
    error_details = [
        ErrorDetail(
            field=" -> ".join(str(loc) for loc in error["loc"]), issue=error["msg"]
        )
        for error in exc.errors()
    ]

    response_payload = ErrorResponse(
        error=ErrorPayload(
            code="VALIDATION_ERROR",
            message="The requested structural parameters failed structural data contract assertions.",
            details=error_details,
        )
    )
    return JSONResponse(
        status_code=422,
        content=response_payload.model_dump(),
    )


# DB Exceptions Hooks ==================================================

db_exceptions = [
    errors.IntegrityError,
    errors.ForeignKeyViolation,
    errors.OperationalError,
]
for db_exec in db_exceptions:
    app.add_exception_handler(db_exec, handle_database_exception)


# Custom Exceptions Hooks ==============================================

custom_exceptions = [
    ChatException,
    ChunkFileException,
    GoogleEmailNotVerifiedException,
    InvalidDocumentTypeException,
    NotFoundException,
    OAuthException
]
for custom_exec in custom_exceptions:
    app.add_exception_handler(custom_exec, handle_custom_exception)
