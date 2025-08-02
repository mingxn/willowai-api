import chromadb
from chromadb.utils import embedding_functions
from src.config import settings

class ChromaDBService:
    def __init__(self):
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(
            name="plant_diseases",
            embedding_function=embedding_functions.OpenAIEmbeddingFunction(
                api_key=settings.OPENAI_API_KEY,
                api_base=settings.OPENAI_BASE_URL,
            )
        )

    def query_disease_info(self, query: str, n_results: int = 1):
        return self.collection.query(
            query_texts=[query],
            n_results=n_results
        )

chroma_service = ChromaDBService()