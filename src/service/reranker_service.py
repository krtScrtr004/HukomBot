from model.chunk_model import ChunkModel
from sentence_transformers import CrossEncoder


class RerankService:

    def __init__(self):
        self.model = CrossEncoder("BAAI/bge-reranker-v2-m3")

    def rerank(self, query: str, chunks: list[ChunkModel]):
        pairs = [(query, chunk.chunk_text) for chunk in chunks]

        scores = self.model.predict(pairs)
        ranked = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)

        return [chunk for chunk, _ in ranked]
