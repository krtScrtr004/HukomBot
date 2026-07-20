from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore"
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
    JWT_ISS: str = "hukom_bot_api"
    JWT_AUD: str = "hukom_bot_frontend"
    JWT_EXP_IN_MIN: int = 30

    # -- Auth --
    OAUTH_CLIENT_ID: str
    OAUTH_CLIENT_SECRET: str

    # -- Google OAuth --
    GOOGLE_OAUTH_REDIRECT_URI: str = (
        "http://127.0.0.1:8000/api/v1/auth/google/login/callback"
    )
    GOOGLE_AUTH_URL: str = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_TOKEN_URL: str = "https://oauth2.googleapis.com/token"

    # -- LLM --
    OPEN_ROUTER_API_KEY: str
    OPEN_ROUTER_MODEL: str = "openrouter/free"
    OPEN_ROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    NVIDIA_API_KEY: str
    NVIDIA_MODEL: str = "z-ai/glm-5.2"
    NVIDIA_BASE_URL: str = "https://integrate.api.nvidia.com/v1"

    # -- Embeding --
    EMBEDDING_MODEL: str = "BAAI/bge-base-en-v1.5"
    EMBEDDING_DEVICE_CPU: str = "cpu"
    EMBEDDING_DEVICE_GPU: str = "cuda"

    # -- Reranker --
    RERANKER_MODEL: str = "BAAI/bge-reranker-v2-m3"
    RERANKER_DEVICE_CPU: str = "cpu"
    RERANKER_DEVICE_GPU: str = "cuda"


settings = Settings()
