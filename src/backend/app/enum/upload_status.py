from enum import Enum

class UploadEnum(str, Enum):
    PENDING = "pending"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    FAILED = "faield"