class AppException(Exception):
    def __init__(self, message: str, status_code: int, code: str, details: list[str]):
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details
        super().__init__(self.message)
        
class UnauthorizedException(AppException):
    def __init__(
        self,
        message: str = "Unauthorized action",
        code: str = "UNAUTHORIZED",
        details: list[str] = [],
    ):
        super().__init__(message, 401, code, details)
        
        
class ForbiddenException(AppException):
    def __init__(
        self,
        message: str = "Forbidden action",
        code: str = "FORBIDDEN",
        details: list[str] = [],
    ):
        super().__init__(message, 403, code, details)
        
class NotFoundException(AppException):
    def __init__(
        self,
        message: str = "Not Found",
        code: str = "NOT_FOUND",
        details: list[str] = [],
    ):
        super().__init__(message, 404, code, details)
