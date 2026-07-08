from enum import StrEnum

class UploadStatus(StrEnum):
    PENDING = "pending"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    FAILED = "failed"