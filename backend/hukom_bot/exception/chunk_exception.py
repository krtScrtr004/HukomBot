from backend.hukom_bot.exception.app_exception import AppException


class ChunkFileException(AppException):
    def __init__(
        self,
        message: str = "Chunks failed to extract.",
        status_code: int = 400,
        code: str = "CHUNK_EXTRACTION_FAILED",
        details: list[str] = [],
    ):
        super().__init__(
            message=message, status_code=status_code, code=code, details=details
        )
