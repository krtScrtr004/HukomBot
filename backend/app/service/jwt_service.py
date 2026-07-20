import jwt

from backend.app.core.settings import settings


class JWTService:
    def __init__(
        self, secret: str = settings.JWT_SECRET, algo: str = settings.JWT_ALGO
    ):
        self._secret = secret
        self._algo = algo

    def encode(self, payload: dict):
        return jwt.encode(payload=payload, key=self._secret, algorithm=self._algo)

    def decode(self, token: str):
        return jwt.decode(jwt=token, key=self._secret, algorithms=[self._algo])
