class InvalidDocumentTypeException(Exception):
    def __init__(self, message: str = "Invalid file type", status_code: int = 422):
        self.message = message
        self.status_code = status_code
        
        super().__init__(self.message)
    