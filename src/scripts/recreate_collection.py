#!/usr/bin/env python3
"""
Recreate Qdrant collection with proper settings to fix internal errors.
"""

from qdrant_client import QdrantClient, models
import time

# Collection settings
COLLECTION_NAME = "science_9_collection"
VECTOR_SIZE = 4096
DISTANCE = "Cosine"

def recreate_collection():
    """Recreate the collection with proper settings."""
    client = QdrantClient(host="localhost", port=6333)
    
    print(f"🔄 Recreating collection: {COLLECTION_NAME}")
    
    # Check if collection exists
    collections = client.get_collections()
    collection_names = [c.name for c in collections.collections]
    
    if COLLECTION_NAME in collection_names:
        print(f"🗑️ Deleting existing collection: {COLLECTION_NAME}")
        client.delete_collection(COLLECTION_NAME)
        time.sleep(1)  # Give it a moment
    
    # Create collection with explicit settings
    print(f"✨ Creating new collection: {COLLECTION_NAME}")
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=VECTOR_SIZE,
            distance=models.Distance.COSINE
        ),
        optimizers_config=models.OptimizersConfigDiff(
            # Add indexing params for better performance
            indexing_threshold=0,  # Index immediately
            memmap_threshold=0     # Use memory mapping from the start
        )
    )
    
    print("✅ Collection created successfully!")
    print("You'll need to reprocess your embeddings to add them to the new collection.")

if __name__ == "__main__":
    recreate_collection()