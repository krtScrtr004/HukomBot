from backend.hukom_bot.exception.app_exception import AppException


class RateLimitException(AppException):
    def __init__(
        self,
        message: str = "Too many requests. Please try again later.",
        details: list[str] = [],
    ):
        super().__init__(message, 429, "RATE_LIMIT_EXCEEDED", details)
