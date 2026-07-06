from enum import StrEnum

class UploadStatus(str, StrEnum):
    PENDING = "pending"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    FAILED = "failed"