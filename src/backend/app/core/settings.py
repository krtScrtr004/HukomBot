import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # -- LLMService --
    LLM_API_KEY: str = os.getenv("OPEN_ROUTER_API_KEY")
    LLM_MODEL: str = "openrouter/free"
    LLM_BASE_URL: str = "https://openrouter.ai/api/v1"
    
    
    # -- EmbedService --
    EMBEDDING_MODEL: str = "BAAI/bge-base-en-v1.5"
    EMBEDDING_DEVICE_CPU: str = "cpu"
    EMBEDDING_DEVICE_GPU: str = "cuda"
        
    # -- RerankService --
    RERANKER_MODEL: str = "BAAI/bge-reranker-v2-m3"
    RERANKER_DEVICE_CPU: str = "cpu"
    RERANKER_DEVICE_GPU: str = "cuda"