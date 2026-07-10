from backend.app.model.chunk_model import Chunk
from sentence_transformers import CrossEncoder


class RerankService:
    def __init__(self):
        self.__model = CrossEncoder("BAAI/bge-reranker-v2-m3")

    def rerank(self, query: str, chunks: list[Chunk]):
        pairs = [(query, chunk.chunk_text) for chunk in chunks]

        scores = self.__model.predict(pairs)
        ranked = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)

        return [chunk for chunk, _ in ranked]
