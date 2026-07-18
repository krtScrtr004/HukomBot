class AppException(Exception):
    def __init__(self, message: str, status_code: int, code: str, details: list[str]):
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details
        super().__init__(self.message)
