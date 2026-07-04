from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend.app.api.v1.endpoint.document import document_router

from backend.app.schema.base_schema import BaseResponse
from backend.app.exception.chunk_exception import ChunkFileException
from backend.app.exception.document_exception import InvalidDocumentTypeException

from backend.app.api.v1.dependency import lifespan
from backend.app.core.logger import setup_logging

setup_logging()

app = FastAPI(lifespan=lifespan)

# Routers
app.include_router(router=document_router, prefix="/document", tags=["document"])


@app.exception_handler(ChunkFileException)
async def invalid_document_type_exception(request: Request, exc: ChunkFileException):
    return JSONResponse(
        status_code=exc.status_code if exc.status_code else 400,
        content=BaseResponse(error=[exc.message]).model_dump(),
    )


@app.exception_handler(InvalidDocumentTypeException)
async def invalid_document_type_exception(
    request: Request, exc: InvalidDocumentTypeException
):
    return JSONResponse(
        status_code=exc.status_code if exc.status_code else 422,
        content=BaseResponse(error=[exc.message]).model_dump(),
    )
