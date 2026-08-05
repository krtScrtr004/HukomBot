from __future__ import annotations

import logging
import numpy as np
from sentence_transformers import SentenceTransformer
import transformers

from backend.hukom_bot.core.settings import settings


# Silence transformer/tokenizer warnings and sentence-transformers progress bars
transformers.logging.set_verbosity_error()
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)


class EmbeddingService:
    _instance: EmbeddingService | None = None

    def __init__(
        self,
        model: str = settings.EMBEDDING_MODEL,
        device: str = settings.EMBEDDING_DEVICE_CPU,
    ):
        self._model = SentenceTransformer(
            model_name_or_path=model,
            device=device,
        )
        # sentence-transformers prints a tqdm bar on every encode by default
        self._model.encode = lambda *a, **k: SentenceTransformer.encode(
            self._model, *a, **k, show_progress_bar=False
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
        max_len = self._model.max_seq_length
        truncated = [doc[:max_len] for doc in documents]
        embeddings = self._model.encode(
            truncated, normalize_embeddings=True
        )
        if isinstance(embeddings, np.ndarray):
            embeddings = embeddings.tolist()
        return embeddings

    def embed_query(self, query: str) -> list[float]:
        formatted_query = (
            "Represent this sentence for searching relevant passages: " + query
        )[: self._model.max_seq_length]
        embedding = self._model.encode(
            formatted_query, normalize_embeddings=True
        )
        return embedding[0].tolist() if len(embedding.shape) > 1 else embedding.tolist()
