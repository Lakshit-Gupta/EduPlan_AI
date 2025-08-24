#!/usr/bin/env python3
"""
Simple semantic search tool for your fixed collection.
"""

import sys
import logging
from src.models.embedding_model import NVEmbedPipeline
from qdrant_client import QdrantClient
# Add this import
from qdrant_client import models

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def search(query_text, collection_name="science_9_collection", limit=3):
    """Search the collection with a text query."""
    print(f"🔍 Searching for: '{query_text}'")
    
    # Generate query embedding
    model = NVEmbedPipeline()
    query_embedding = model.embed_query(query_text)
    print(f"Generated embedding of dimension {len(query_embedding)}")
    
    # Connect to Qdrant
    client = QdrantClient(host="localhost", port=6333)
    
    # Search collection
    try:
        results = client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=limit,
            with_payload=True
        )
        
        print(f"\n📊 Found {len(results)} results:")
        
        for i, result in enumerate(results):
            print(f"\n{i+1}. Score: {result.score:.4f}")
            
            metadata = result.payload.get("metadata", {})
            text = result.payload.get("text", "")
            
            print(f"   ID: {result.id}")
            print(f"   Chapter: {metadata.get('chapter', 'Unknown')}")
            print(f"   Section: {metadata.get('section', 'Unknown')}")
            
            # Preview text
            preview = text[:150] + "..." if len(text) > 150 else text
            print(f"   Text preview: {preview}")
            
    except Exception as e:
        print(f"❌ Error searching: {e}")
        logger.error(f"Error details: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = input("Enter search query: ")
    
    search(query)