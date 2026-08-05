from enum import StrEnum

class OAuthProvider(StrEnum):
    GOOGLE = "google"
    FACEBOOK = "facebook"
    APPLE = "apple"
    
    def display_name(self):
        match self:
            case OAuthProvider.GOOGLE:
                return "Google"
            case OAuthProvider.FACEBOOK:
                return "Facebook"
            case OAuthProvider.APPLE:
                return "Apple"