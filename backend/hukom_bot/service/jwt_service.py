import jwt
import logging

from backend.hukom_bot.core.settings import settings
from backend.hukom_bot.schema.auth_schema import JWTPayload

logger = logging.getLogger(__name__)


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
        return jwt.encode(
            payload=payload.model_dump(), key=self._secret, algorithm=self._algo
        )

    def verify(
        self,
        token: str,
    ):
        try:
            return jwt.decode(
                jwt=token,
                key=self._secret,
                algorithms=[self._algo],
                issuer=self._iss,
                audience=self._aud,
            )
        except Exception as ex:
            logger.warning("Someone has tried to use invalid JWT token: %s", str(ex))
            raise
