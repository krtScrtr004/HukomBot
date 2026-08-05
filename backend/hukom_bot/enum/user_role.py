from enum import StrEnum

class UserRole(StrEnum):
    STANDARD = "standard"
    CONTRIBUTOR = "contributor",
    ADMIN = "admin"