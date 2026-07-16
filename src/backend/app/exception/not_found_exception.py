from backend.app.exception.app_exception import AppException


class NotFoundException(AppException):
    def __init__(self, message: str = "Not Found", code: str = "ENTITY_NOT_FOUND"):
        super().__init__(message, 404, code)
