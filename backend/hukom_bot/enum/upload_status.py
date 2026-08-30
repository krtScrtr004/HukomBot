from enum import StrEnum

class UploadStatus(StrEnum):
    FAILED = "failed"
    REJECTED = "rejected"
    PENDING = "pending"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    
    def display_name(self) -> str:
        match self:
            case UploadStatus.FAILED:
                return "Failed"
            case UploadStatus.REJECTED:
                return "Rejected"
            case UploadStatus.PENDING:
                return "Pending"
            case UploadStatus.ONGOING:
                return "Ongoing"
            case UploadStatus.COMPLETED:
                return "Completed"
            
    def get_level(self) -> int:
        match self:
            case UploadStatus.FAILED:
                return -2
            case UploadStatus.REJECTED:
                return -1
            case UploadStatus.PENDING:
                return 0
            case UploadStatus.ONGOING:
                return 1
            case UploadStatus.COMPLETED:
                return 2