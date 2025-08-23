from typing import List
import sys
import os
from sentence_transformers import SentenceTransformer

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.config import EMBEDDING_MODEL, BATCH_SIZE

class DocumentEmbeddings:
    """
    Class for encoding text using SentenceTransformers models
    """
    
    def __init__(self, model_name: str = None):
        """
        Initialize the embedding model
        
        Args:
            model_name: Name of the sentence transformer model
        """
        # Use a reliable sentence transformer model
        self.model_name = model_name or "all-MiniLM-L6-v2"
        
        # Load the sentence transformer model
        self.model = SentenceTransformer(self.model_name)
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        # SentenceTransformers handles batching internally
        embeddings = self.model.encode(
            texts,
            batch_size=BATCH_SIZE,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        # Convert to list of lists for consistency
        return embeddings.tolist()
    
    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a single query text
        
        Args:
            query: Text to embed
            
        Returns:
            Embedding vector
        """
        return self.embed_texts([query])[0]
    
    @property
    def embedding_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors
        
        Returns:
            Dimension of embeddings
        """
        return self.model.get_sentence_embedding_dimension()
