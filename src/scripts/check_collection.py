#!/usr/bin/env python3
"""
Check Qdrant collection status.
This script provides information about your collection.
"""

import sys
import os
from qdrant_client import QdrantClient

# Collection name to check
COLLECTION_NAME = "science_9_collection"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

def check_collection(collection_name=COLLECTION_NAME):
    """Check collection status and display info."""
    print(f"🔍 Checking collection: {collection_name}")
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    
    try:
        # Check if collection exists
        collections = client.get_collections()
        collection_names = [c.name for c in collections.collections]
        print(f"Available collections: {collection_names}")
        
        if collection_name not in collection_names:
            print(f"❌ Collection '{collection_name}' not found!")
            return
        
        # Get collection info
        info = client.get_collection(collection_name)
        vector_size = info.config.params.vectors.size
        distance = info.config.params.vectors.distance
        
        print(f"✅ Collection '{collection_name}' exists")
        print(f"   Vector size: {vector_size}")
        print(f"   Distance metric: {distance}")
        
        # Count points
        count = client.count(collection_name).count
        print(f"   Number of points: {count}")
        
        if count > 0:
            # Try to search for a random point to verify
            dummy_vector = [0.0] * vector_size
            try:
                results = client.search(
                    collection_name=collection_name,
                    query_vector=dummy_vector,
                    limit=1,
                    with_payload=True
                )
                
                if results:
                    print("✅ Search operation successful")
                    print(f"   Sample point ID: {results[0].id}")
            except Exception as e:
                print(f"❌ Search failed: {e}")
        
    except Exception as e:
        print(f"❌ Error checking collection: {e}")
        
if __name__ == "__main__":
    check_collection()