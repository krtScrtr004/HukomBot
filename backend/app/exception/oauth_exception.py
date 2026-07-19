from backend.app.exception.app_exception import AppException


class OAuthException(AppException):
    def __init__(
        self,
        message: str = "OAuth service fail",
        status_code: int = 422,
        code: str = "OAUTH_FAIL",
        details: list[str] = [],
    ):
        super().__init__(message, status_code, code, details)

class GoogleEmailNotVerifiedException(AppException):
    def __init__(
        self,
        message: str = "Google email is not verified",
        code: str = "GOOGLE_EMAIL_NOT_VERIFIED",
        details: list[str] = [],
    ):
        super().__init__(message, 400, code, details)
