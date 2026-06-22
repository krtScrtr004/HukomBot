from sentence_transformers import SentenceTransformer

class EmbedService:
    MODEL = "BAAI/bge-base-en-v1.5"

    def __init__(self):
        self.__model = SentenceTransformer(
            model_name_or_path = EmbedService.MODEL
        )


    def embed_documents(self, documents: list[str]):
        return self.__model.encode(
            inputs = documents,
            normalize_embeddings = True
        )


    def embed_query(self, query: str):
        formatted_query = (
            "Represent this sentence for searching relevant passages: "
            + query
        )

        return self.__model.encode(
            formatted_query,
            normalize_embeddings = True
        )[0]