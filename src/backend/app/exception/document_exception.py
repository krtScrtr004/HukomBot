from backend.app.exception.app_exception import AppException


class InvalidDocumentTypeException(AppException):
    def __init__(
        self,
        message: str = "Invalid file type",
        status_code: int = 422,
        code: str = "INVALID_FILE_TYPE",
    ):
        super().__init__(message, status_code, code)
