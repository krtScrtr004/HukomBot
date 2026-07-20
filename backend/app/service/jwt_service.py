import jwt

from backend.app.core.settings import settings
from backend.app.schema.auth_schema import JWTPayload


class JWTService:
    def __init__(
        self,
        secret: str = settings.JWT_SECRET,
        algo: str = settings.JWT_ALGO,
        iss: str = settings.JWT_ISS,
        aud: str = settings.JWT_AUD,
    ):
        self._secret = secret
        self._algo = algo
        self._iss = iss
        self._aud = aud

    def encode(self, payload: JWTPayload):
        return jwt.encode(payload=payload, key=self._secret, algorithm=self._algo)

    def verify(
        self,
        token: str,
    ):
        decoded = jwt.decode(jwt=token, key=self._secret, algorithms=[self._algo])
        payload = JWTPayload.model_validate(decoded["payload"])

        if payload.iss != self._iss:
            raise jwt.InvalidTokenError("Invalid token issuer")

        if payload.aud != self._aud:
            raise jwt.InvalidTokenError("Invalid token audience")
