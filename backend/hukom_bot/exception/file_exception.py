from backend.hukom_bot.exception.app_exception import AppException


class InvalidFileTypeException(AppException):
    def __init__(
        self,
        message: str = "Invalid file type",
        status_code: int = 422,
        code: str = "INVALID_FILE_TYPE",
        details: list[str] = [],
    ):
        super().__init__(
            message=message, status_code=status_code, code=code, details=details
        )
        
class FileSizeTooLargeException(AppException):
    def __init__(
            self,
            message: str = "File size too large",
            status_code: int = 422,
            code: str = "FILE_SIZE_TOO_LARGE",
            details: list[str] = [],
        ):
            super().__init__(
                message=message, status_code=status_code, code=code, details=details
            )
