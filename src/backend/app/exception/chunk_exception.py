class ChunkFileException(Exception):
    def __init__(self, message: str = "Chunks fail to extract", status_code = 400):
        self.message = message
        self.status_code = status_code
        
        super().__init__(self.message)