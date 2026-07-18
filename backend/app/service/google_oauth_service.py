from urllib.parse import urlencode
from fastapi.responses import RedirectResponse
from backend.app.core.settings import Settings


class GoogleOAuthService:
    def redirect_to_authorization(self):
        params = {
            "client_id": Settings.OAUTH_CLIENT_ID,
            "redirect_uri": Settings.GOOGLE_OAUTH_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
        }
        url = urlencode(params)
        
        google_url = Settings.GOOGLE_AUTH_URL + "?" + urlencode(params)
        return RedirectResponse(google_url)        
