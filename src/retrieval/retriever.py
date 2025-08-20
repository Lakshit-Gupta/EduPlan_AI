from typing import List, Dict, Any
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from database.qdrant_connector import QdrantDB
from embedding.nv_embed import NVEmbeddings

class DocumentRetriever:
    """
    Retrieval system for finding relevant documents based on queries
    """
    
    def __init__(self):
        """Initialize the retrieval system with database and embedding model"""
        self.db = QdrantDB()
        self.embedder = NVEmbeddings()
    
    def retrieve(
        self, 
        query: str, 
        top_k: int = None,
        filter_class: str = None,
        filter_subject: str = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query
        
        Args:
            query: User query string
            top_k: Number of documents to retrieve
            filter_class: Optional class filter
            filter_subject: Optional subject filter
            
        Returns:
            List of relevant documents with metadata and scores
        """
        # Generate embedding for the query
        query_embedding = self.embedder.embed_query(query)
        
        # Search for similar documents
        results = self.db.search_documents(
            query_embedding=query_embedding,
            top_k=top_k,
            filter_class=filter_class
        )
        
        # Apply subject filter if needed (done here as Qdrant has limited filter options)
        if filter_subject and results:
            results = [doc for doc in results if doc.get("subject") == filter_subject]
            
            # Limit to top_k again after filtering
            if top_k and len(results) > top_k:
                results = results[:top_k]
        
        return results
