from backend.hukom_bot.model.chunk_model import Chunk
from backend.hukom_bot.schema.chunk_schema import ChunkCreate


class ChunkCaster:
    
    @staticmethod
    def create_to_base(chunk: ChunkCreate) -> Chunk:
        return Chunk(
            id=chunk.id,
            document_id=chunk.document_id,
            chunk_number=chunk.chunk_number,
            chunk_text=chunk.chunk_text,
            section=chunk.section,
            embedding=chunk.embedding,
        )