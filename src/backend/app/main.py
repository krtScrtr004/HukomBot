from psycopg import errors
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

from backend.app.api.v1.endpoint.document import document_api_router

from backend.app.schema.base_schema import BaseResponse
from backend.app.exception.chunk_exception import ChunkFileException
from backend.app.exception.document_exception import InvalidDocumentTypeException
from backend.app.exception.chat_exception import ChatException

from backend.app.api.v1.dependency import lifespan
from backend.app.core.logger import setup_logging

setup_logging()

app = FastAPI(lifespan=lifespan)

# Routers ============================================================
app.include_router(
    router=document_api_router, prefix="/api/documents", tags=["Documents API"]
)

# Exception Handlers ==================================================

async def handle_database_exception(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=BaseResponse(errors=[f"Database error: {str(exc)}"]).model_dump(),
    )
    
async def handle_custom_exception(request: Request, exc: Exception):
    return JSONResponse(
        status_code=exc.status_code,
        content=BaseResponse(errors=[exc.message]).model_dump(),
    )

# Exceptions ===========================================================

@app.exception_handler(Exception)
async def http_exception(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=BaseResponse(errors=[str(exc)]).model_dump(),
    )

@app.exception_handler(HTTPException)
async def http_exception(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=BaseResponse(errors=[exc.detail]).model_dump(),
    )

# DB Exceptions =========================================================

db_exceptions = [
    errors.IntegrityError,
    errors.ForeignKeyViolation,
    errors.OperationalError,
]
for db_exec in db_exceptions:
    app.add_exception_handler(db_exec, handle_database_exception)

# Custom Exceptions =====================================================

custom_exceptions = [
    ChatException,
    ChunkFileException,
    InvalidDocumentTypeException
]

for custom_exec in custom_exceptions:
    app.add_exception_handler(custom_exec, handle_custom_exception)
