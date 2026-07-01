class InvalidDocumentTypeException(Exception):
    def __init__(self, message: str = "Invalid file type"):
        self.message = message
        super().__init__(self.message)
    