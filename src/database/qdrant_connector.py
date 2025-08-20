from typing import List, Dict, Any
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class QdrantDB:
    """
    Qdrant vector database connector for storing and retrieving embeddings
    """
    
    def __init__(self, host: str = None, port: int = None, collection_name: str = None):
        """
        Initialize the Qdrant client
        
        Args:
            host: Qdrant server host
            port: Qdrant server port
            collection_name: Collection to store embeddings
        """
        self.host = host or config.QDRANT_HOST
        self.port = port or config.QDRANT_PORT
        self.collection_name = collection_name or config.QDRANT_COLLECTION_NAME
        self.vector_size = config.QDRANT_VECTOR_SIZE
        
        # Connect to Qdrant
        self.client = QdrantClient(host=self.host, port=self.port)
        
    def create_collection(self) -> None:
        """Create collection if it doesn't exist"""
        # Check if collection exists
        collections = self.client.get_collections().collections
        collection_names = [collection.name for collection in collections]
        
        if self.collection_name not in collection_names:
            # Create new collection
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.vector_size,
                    distance=models.Distance.COSINE,
                ),
                # Add a payload field filter for class filtering
                sparse_vectors_config={},
            )
            print(f"Collection '{self.collection_name}' created successfully")
        else:
            print(f"Collection '{self.collection_name}' already exists")
    
    def insert_documents(
        self, embeddings: List[List[float]], documents: List[str], metadata: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Insert document embeddings into Qdrant
        
        Args:
            embeddings: List of document embeddings
            documents: List of document texts
            metadata: List of document metadata
            
        Returns:
            List of inserted document IDs
        """
        # Make sure collection exists
        self.create_collection()
        
        # Prepare points for insertion
        points = []
        for i, (embedding, document, meta) in enumerate(zip(embeddings, documents, metadata)):
            point_id = len(documents) * 10000 + i  # Simple ID generation
            
            points.append(
                models.PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "text": document,
                        "class": meta.get("class", "unknown"),
                        "subject": meta.get("subject", "unknown"),
                        "topic": meta.get("topic", "unknown"),
                        "difficulty": meta.get("difficulty", "basic"),
                        "filename": meta.get("filename", "unknown"),
                        "created_at": meta.get("created_at"),
                        "updated_at": meta.get("updated_at")
                    }
                )
            )
        
        # Insert points in batches
        batch_size = config.BATCH_SIZE
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch
            )
        
        # Return IDs
        return [str(point.id) for point in points]
    
    def search_documents(
        self, 
        query_embedding: List[float], 
        top_k: int = None,
        filter_class: str = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents
        
        Args:
            query_embedding: Embedding of the query
            top_k: Number of results to return
            filter_class: Optional filter by class
            
        Returns:
            List of search results with documents and metadata
        """
        if top_k is None:
            top_k = config.TOP_K_RESULTS
            
        # Prepare filter
        filter_dict = {}
        if filter_class:
            filter_dict["class"] = filter_class
            
        # Search with filters if needed
        search_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key=key,
                    match=models.MatchValue(value=value)
                )
                for key, value in filter_dict.items()
            ]
        ) if filter_dict else None
        
        # Search for similar documents
        search_results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k,
            query_filter=search_filter,
            with_payload=True,
            with_vectors=False,
        )
        
        # Format results
        results = []
        for result in search_results:
            results.append({
                "id": result.id,
                "text": result.payload.get("text", ""),
                "score": result.score,
                "class": result.payload.get("class", ""),
                "subject": result.payload.get("subject", ""),
                "topic": result.payload.get("topic", ""),
                "difficulty": result.payload.get("difficulty", ""),
                "filename": result.payload.get("filename", "")
            })
        
        return results
