from backend.app.exception.app_exception import AppException


class ChatException(AppException):
    def __init__(
        self,
        message: str = "Chat pipeline fails",
        status_code=500,
        code: str = "CHAT_PIPELINE_FAILED",
    ):
        super().__init__(message, status_code, code)
