from backend.app.exception.app_exception import AppException


class ChunkFileException(AppException):
    def __init__(
        self,
        message: str = "Chunks failed to extract.",
        status_code: int = 400,
        code: str = "CHUNK_EXTRACTION_FAILED",  # <-- Added a machine-readable code
    ):
        super().__init__(message, status_code, code)
