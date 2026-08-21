class AppException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int,
        code: str,
        headers: dict[str, any] = {},
        details: list[str] = [],
    ):
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details
        self.headers = headers
        super().__init__(self.message)


class UnauthorizedException(AppException):
    def __init__(
        self,
        message: str = "Unauthorized action",
        code: str = "UNAUTHORIZED",
        details: list[str] = [],
    ):
        super().__init__(message=message, statuc_code=401, code=code, details=details)


class ForbiddenException(AppException):
    def __init__(
        self,
        message: str = "Forbidden action",
        code: str = "FORBIDDEN",
        details: list[str] = [],
    ):
        super().__init__(message=message, status_coed=403, code=code, details=details)


class NotFoundException(AppException):
    def __init__(
        self,
        message: str = "Not Found",
        code: str = "NOT_FOUND",
        details: list[str] = [],
    ):
        super().__init__(message=message, statuc_code=404, code=code, details=details)


class RateLimitException(AppException):
    def __init__(
        self,
        message: str = "Too many requests. Please try again later.",
        code: str = "RATE_LIMIT_EXCEEDED",
        headers: dict[str, any] = {},
        details: list[str] = [],
    ):
        super().__init__(
            message=message,
            status_code=429,
            code=code,
            headers=headers,
            details=details,
        )

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