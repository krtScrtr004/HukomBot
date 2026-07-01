from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend.app.schema.base_schema import Response
from backend.app.exception.document_exception import InvalidDocumentTypeException

app = FastAPI()


@app.exception_handler(InvalidDocumentTypeException)
async def invalid_document_type_exception(
    request: Request, exc: InvalidDocumentTypeException
):
    return JSONResponse(
        status_code=422, content=Response(error=[exc.message]).model_dump()
    )
