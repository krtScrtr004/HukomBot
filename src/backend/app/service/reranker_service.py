from __future__ import annotations
from sentence_transformers import CrossEncoder
from backend.app.model.chunk_model import Chunk

from backend.app.core.settings import Settings


class RerankerService:
    _instance: RerankerService | None = None

    def __init__(
        self,
        model: str = Settings.RERANKER_MODEL,
        device: str = Settings.RERANKER_DEVICE_CPU,
    ):
        self.__model = CrossEncoder(model_name_or_path=model, device=device)

    @classmethod
    def initialize(cls) -> RerankerService:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def get_instance(cls) -> RerankerService:
        if cls._instance is None:
            return RuntimeError("Rerank service is not initialized")
        return cls._instance

    def rerank(self, query: str, chunks: list[Chunk]):
        pairs = [(query, chunk.chunk_text) for chunk in chunks]

        scores = self.__model.predict(pairs)
        ranked = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)

        return [chunk for chunk, _ in ranked]
