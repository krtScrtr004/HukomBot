from __future__ import annotations

import numpy as np
from sentence_transformers import SentenceTransformer

from backend.app.core.settings import Settings


class EmbeddingService:
    _instance: EmbeddingService | None = None

    def __init__(
        self,
        model: str = Settings.EMBEDDING_MODEL,
        device: str = Settings.EMBEDDING_DEVICE_CPU,
    ):
        self._model = SentenceTransformer(
            model_name_or_path=model,
            device=device,
        )

    @classmethod
    def initialize(cls) -> EmbeddingService:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def get_instance(cls) -> EmbeddingService:
        if cls._instance is None:
            return RuntimeError("Embed service is not initialized")
        return cls._instance

    def embed_documents(self, documents: list[str]) -> list[list[float]]:
        embeddings = self._model.encode(documents, normalize_embeddings=True)
        if isinstance(embeddings, np.ndarray):
            embeddings = embeddings.tolist()
        return embeddings

    def embed_query(self, query: str) -> list[float]:
        formatted_query = (
            "Represent this sentence for searching relevant passages: " + query
        )
        embedding = self._model.encode(formatted_query, normalize_embeddings=True)
        return embedding[0].tolist() if len(embedding.shape) > 1 else embedding.tolist()
