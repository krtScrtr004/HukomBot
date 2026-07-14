class NotFoundException(Exception):
    def __init__(self, message: str = "Not Found"):
        self.message = message
        self.status_code = 404
        
        super().__init__(self.message)