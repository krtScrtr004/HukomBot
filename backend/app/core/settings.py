import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    JWT_SECRET: str = os.getenv("JWT_SECRET")
    
    # -- AuthServices  --
    OAUTH_CLIENT_ID: str = os.getenv("OAUTH_CLIENT_ID")
    OAUTH_CLIENT_SECRET: str = os.getenv("OAUTH_CLIENT_SECRET")
    
    # -- AuthServices  --
    GOOGLE_OAUTH_REDIRECT_URI: str = os.getenv("GOOGLE_OAUTH_REDIRECT_URI")
    GOOGLE_AUTH_URL: str = os.getenv("GOOGLE_AUTH_URL")
    GOOGLE_TOKEN_URL: str = os.getenv("GOOGLE_TOKEN_URL")
    
    
    # -- LLMService --
    OPEN_ROUTER_API_KEY: str = os.getenv("OPEN_ROUTER_API_KEY")
    OPEN_ROUTER_MODEL: str = "openrouter/free"
    OPEN_ROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    
    NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY")
    NVIDIA_MODEL: str = "z-ai/glm-5.2"
    NVIDIA_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    
    
    # -- EmbedService --
    EMBEDDING_MODEL: str = "BAAI/bge-base-en-v1.5"
    EMBEDDING_DEVICE_CPU: str = "cpu"
    EMBEDDING_DEVICE_GPU: str = "cuda"
        
    # -- RerankService --
    RERANKER_MODEL: str = "BAAI/bge-reranker-v2-m3"
    RERANKER_DEVICE_CPU: str = "cpu"
    RERANKER_DEVICE_GPU: str = "cuda"