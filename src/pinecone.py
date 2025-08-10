from pinecone import Pinecone, ServerlessSpec
from src.config import settings
from src.diagnose.utils import get_embedding
from typing import Dict, List, Optional
import uuid
import time

class PineconeService:
    def __init__(self):
        self.client = None
        self.index = None
        self.index_name = settings.PINECONE_INDEX_NAME
        self._initialized = False

    def _initialize_index(self):
        """Initialize or create the Pinecone index if it doesn't exist."""
        if self._initialized:
            return
            
        try:
            # Skip initialization if using placeholder API key
            if settings.PINECONE_API_KEY in ["your-pinecone-api-key", "your_pinecone_api_key_here"]:
                print("Warning: Using placeholder Pinecone API key. Skipping initialization.")
                return
                
            self.client = Pinecone(api_key=settings.PINECONE_API_KEY)
            
            # Check if index exists
            existing_indexes = self.client.list_indexes()
            index_names = [index.name for index in existing_indexes]
            
            if self.index_name not in index_names:
                # Create index with dimensions for text-embedding-3-small (1536 dimensions)
                self.client.create_index(
                    name=self.index_name,
                    dimension=1536,  # text-embedding-3-small dimensions
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region=settings.PINECONE_ENVIRONMENT
                    )
                )
                # Wait for index to be ready
                time.sleep(5)
            
            self.index = self.client.Index(self.index_name)
            self._initialized = True
            
        except Exception as e:
            print(f"Error initializing Pinecone index: {e}")
            print("Pinecone service will not be available until a valid API key is configured.")

    def _ensure_initialized(self):
        """Ensure the service is initialized before use."""
        if not self._initialized:
            self._initialize_index()
            
        if not self._initialized:
            raise RuntimeError("Pinecone service is not initialized. Please check your API key configuration.")

    def query_disease_info(self, query: str, n_results: int = 1) -> Dict:
        """
        Query disease information from Pinecone.
        
        Args:
            query (str): The search query
            n_results (int): Number of results to return
            
        Returns:
            Dict: Query results in ChromaDB-compatible format
        """
        try:
            self._ensure_initialized()
            query_embedding = get_embedding(query)
            
            # Query Pinecone
            response = self.index.query(
                vector=query_embedding,
                top_k=n_results,
                include_metadata=True,
                include_values=False
            )
            
            # Convert to ChromaDB-compatible format
            documents = []
            metadatas = []
            ids = []
            distances = []
            
            for match in response.matches:
                documents.append(match.metadata.get('document', ''))
                metadatas.append({
                    'plant_name': match.metadata.get('plant_name', ''),
                    'condition': match.metadata.get('condition', '')
                })
                ids.append(match.id)
                distances.append(1 - match.score)  # Convert similarity to distance
            
            return {
                'documents': [documents] if documents else [[]],
                'metadatas': [metadatas] if metadatas else [[]],
                'ids': [ids] if ids else [[]],
                'distances': [distances] if distances else [[]]
            }
        except Exception as e:
            print(f"Error querying Pinecone: {e}")
            return {
                'documents': [[]],
                'metadatas': [[]],
                'ids': [[]],
                'distances': [[]]
            }

    def add_disease_info(self, disease_info: Dict):
        """
        Add disease information to Pinecone.
        
        Args:
            disease_info (Dict): Dictionary with 'document', 'metadata', and 'id' keys
        """
        try:
            self._ensure_initialized()
            
            # Generate embedding for the document
            document_embedding = get_embedding(disease_info["document"])
            
            # Prepare metadata for Pinecone (flatten the structure)
            pinecone_metadata = {
                'document': disease_info["document"],
                'plant_name': disease_info["metadata"].get('plant_name', ''),
                'condition': disease_info["metadata"].get('condition', '')
            }
            
            # Upsert to Pinecone
            self.index.upsert([
                {
                    'id': disease_info["id"],
                    'values': document_embedding,
                    'metadata': pinecone_metadata
                }
            ])
            
        except Exception as e:
            print(f"Error adding to Pinecone: {e}")
            raise

    def delete_disease_info(self, doc_id: str):
        """
        Delete a document from Pinecone.
        
        Args:
            doc_id (str): The ID of the document to delete
        """
        try:
            self._ensure_initialized()
            self.index.delete(ids=[doc_id])
        except Exception as e:
            print(f"Error deleting from Pinecone: {e}")
            raise

    def list_all_ids(self) -> List[str]:
        """
        List all document IDs in the index.
        Note: This is a simplified implementation for small datasets.
        For large datasets, consider implementing pagination.
        """
        try:
            self._ensure_initialized()
            
            # This is a workaround since Pinecone doesn't have a direct list_ids method
            # We'll query with a dummy vector to get all results
            dummy_vector = [0.0] * 1536
            response = self.index.query(
                vector=dummy_vector,
                top_k=10000,  # Adjust based on your dataset size
                include_metadata=False,
                include_values=False
            )
            return [match.id for match in response.matches]
        except Exception as e:
            print(f"Error listing IDs: {e}")
            return []

# Initialize the Pinecone service instance
pinecone_service = PineconeService()
