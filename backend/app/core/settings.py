from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore",
    }

    # -- Database --
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    # -- JWT --
    JWT_SECRET: str
    JWT_ALGO: str
    JWT_ISS: str
    JWT_AUD: str
    JWT_EXP_IN_MIN: int

    # -- Auth --
    OAUTH_CLIENT_ID: str
    OAUTH_CLIENT_SECRET: str

    # -- Google OAuth --
    GOOGLE_OAUTH_REDIRECT_URI: str
    GOOGLE_AUTH_URL: str
    GOOGLE_TOKEN_URL: str

    # -- LLM --
    OPEN_ROUTER_API_KEY: str
    OPEN_ROUTER_MODEL: str
    OPEN_ROUTER_BASE_URL: str

    NVIDIA_API_KEY: str
    NVIDIA_MODEL: str
    NVIDIA_BASE_URL: str

    # -- Embeding --
    EMBEDDING_MODEL: str
    EMBEDDING_DEVICE_CPU: str
    EMBEDDING_DEVICE_GPU: str

    # -- Reranker --
    RERANKER_MODEL: str
    RERANKER_DEVICE_CPU: str
    RERANKER_DEVICE_GPU: str


settings = Settings()
