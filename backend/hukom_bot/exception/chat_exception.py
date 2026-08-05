from backend.hukom_bot.exception.app_exception import AppException


class ChatException(AppException):
    def __init__(
        self,
        message: str = "Chat pipeline fails",
        status_code=500,
        code: str = "CHAT_PIPELINE_FAILED",
        details: list[str] = [],
    ):
        super().__init__(message, status_code, code, details)
