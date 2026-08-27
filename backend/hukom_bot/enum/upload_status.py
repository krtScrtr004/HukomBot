from enum import StrEnum

class UploadStatus(StrEnum):
    PENDING = "pending"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    FAILED = "failed"
    
    def display_name(self) -> str:
        match self:
            case UploadStatus.PENDING:
                return "Pending"
            case UploadStatus.ONGOING:
                return "Ongoing"
            case UploadStatus.COMPLETED:
                return "Completed"
            case UploadStatus.FAILED:
                return "Failed"    
            
    def get_level(self) -> int:
        match self:
            case UploadStatus.PENDING:
                return 0
            case UploadStatus.ONGOING:
                return 1
            case UploadStatus.COMPLETED:
                return 2
            case UploadStatus.FAILED:
                return 3    