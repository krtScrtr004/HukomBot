from __future__ import annotations
from sentence_transformers import CrossEncoder
from backend.app.model.chunk_model import Chunk


class RerankService:
    __instance = RerankService|None = None
    def __init__(self):
        self.__model = CrossEncoder("BAAI/bge-reranker-v2-m3")
        
    @classmethod
    def initialize(cls) -> RerankService:
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance
    
    @classmethod
    def get_instance(cls) -> RerankService:
        if cls.__instance is None:
            return RuntimeError("Rerank service is not initialized")
        return cls.__instance

    def rerank(self, query: str, chunks: list[Chunk]):
        pairs = [(query, chunk.chunk_text) for chunk in chunks]

        scores = self.__model.predict(pairs)
        ranked = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)

        return [chunk for chunk, _ in ranked]
