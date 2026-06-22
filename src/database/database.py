import os
import chromadb
from chromadb import Collection
from util.utility import get_project_root

class Database:
    COLLECTION_PATH = get_project_root() / "chroma"
    COLLECTION_NAME = "collection"

    def __init__(self):
        self._chroma_client = chromadb.PersistentClient(
            path = self.COLLECTION_PATH
        )


    def get_or_create_collection(self) -> Collection:
        return self._chroma_client.get_or_create_collection(name = self.COLLECTION_NAME)
