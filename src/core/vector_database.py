from typing import List, Dict, Any
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models
from .config import QDRANT_HOST, QDRANT_PORT, QDRANT_COLLECTION_NAME

class QdrantDB:
    """Qdrant vector database connector for storing and retrieving embeddings"""
    
    def __init__(self, vector_size: int = None):
        self.host = QDRANT_HOST
        self.port = QDRANT_PORT
        self.collection_name = QDRANT_COLLECTION_NAME
        self.vector_size = vector_size  # Will be set dynamically based on embeddings
        
        # Connect to Qdrant
        self.client = QdrantClient(host=self.host, port=self.port)
        print(f"✅ Connected to Qdrant at {self.host}:{self.port}")
        
    def create_collection(self, vector_size: int) -> None:
        """Create collection if it doesn't exist with dynamic vector size"""
        self.vector_size = vector_size
        try:
            collections = self.client.get_collections().collections
            collection_names = [collection.name for collection in collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=self.vector_size,
                        distance=models.Distance.COSINE,
                    ),
                )
                print(f"✅ Collection '{self.collection_name}' created with vector size {self.vector_size}")
            else:
                print(f"✅ Collection '{self.collection_name}' already exists")
        except Exception as e:
            print(f"❌ Error creating collection: {e}")
    
    def insert_documents(self, embeddings: List[List[float]], documents: List[str], metadata: List[Dict[str, Any]]) -> List[str]:
        """Insert document embeddings into Qdrant"""
        # Create collection with correct vector size
        if embeddings:
            vector_size = len(embeddings[0])
            self.create_collection(vector_size)
        
        points = []
        for i, (embedding, document, meta) in enumerate(zip(embeddings, documents, metadata)):
            point_id = i + 1000  # Simple ID generation
            
            points.append(
                models.PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "text": document,
                        "chapter": meta.get("chapter", "unknown"),
                        "subject": meta.get("subject", "unknown"),
                        "difficulty": meta.get("difficulty", "Basic"),
                        "source_file": meta.get("source_file", "unknown"),
                        "chunk_index": meta.get("chunk_index", 0)
                    }
                )
            )
        
        # Insert points in batches
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.client.upsert(collection_name=self.collection_name, points=batch)
        
        print(f"✅ Inserted {len(points)} documents into Qdrant")
        return [str(point.id) for point in points]
    
    def search_documents(self, query_embedding: List[float], top_k: int = 5, filter_chapter: str = None, filter_subject: str = None) -> List[Dict[str, Any]]:
        """Search for similar documents with chapter and subject filtering"""
        # Prepare filter
        filter_conditions = []
        if filter_chapter:
            filter_conditions.append(
                models.FieldCondition(
                    key="chapter",
                    match=models.MatchValue(value=filter_chapter)
                )
            )
        if filter_subject:
            filter_conditions.append(
                models.FieldCondition(
                    key="subject", 
                    match=models.MatchValue(value=filter_subject)
                )
            )
        
        search_filter = models.Filter(must=filter_conditions) if filter_conditions else None
        
        # Search for similar documents
        search_results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k,
            query_filter=search_filter,
            with_payload=True,
        )
        
        # Format results
        results = []
        for result in search_results:
            results.append({
                "id": result.id,
                "text": result.payload.get("text", ""),
                "score": result.score,
                "chapter": result.payload.get("chapter", ""),
                "subject": result.payload.get("subject", ""),
                "difficulty": result.payload.get("difficulty", ""),
                "source_file": result.payload.get("source_file", "")
            })
        
        return results
