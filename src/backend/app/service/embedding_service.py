from __future__ import annotations

import numpy as np
from sentence_transformers import SentenceTransformer

from backend.app.core.settings import Settings


class EmbeddingService:
    __instance: EmbeddingService | None = None

    def __init__(
        self,
        model: str = Settings.EMBEDDING_MODEL,
        device: str = Settings.EMBEDDING_DEVICE_CPU,
    ):
        self.__model = SentenceTransformer(
            model_name_or_path=model,
            device=device,
        )

    @classmethod
    def initialize(cls) -> EmbeddingService:
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    @classmethod
    def get_instance(cls) -> EmbeddingService:
        if cls.__instance is None:
            return RuntimeError("Embed service is not initialized")
        return cls.__instance

    def embed_documents(self, documents: list[str]) -> list[list[float]]:
        embeddings = self.__model.encode(documents, normalize_embeddings=True)
        if isinstance(embeddings, np.ndarray):
            embeddings = embeddings.tolist()
        return embeddings

    def embed_query(self, query: str) -> list[float]:
        formatted_query = (
            "Represent this sentence for searching relevant passages: " + query
        )
        embedding = self.__model.encode(formatted_query, normalize_embeddings=True)
        return embedding[0].tolist() if len(embedding.shape) > 1 else embedding.tolist()
