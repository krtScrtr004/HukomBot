class CaseAnalysisVersionNotFound(Exception):
    def __init__(self, message: str = "Case analysis not found"):
        self.message = message
        self.status_code = 404
        
        super().__init__(self.message)
