#!/usr/bin/env python3
"""
Test script to verify Qdrant is working properly.
"""

from qdrant_client import QdrantClient, models
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test collection name
TEST_COLLECTION = "test_collection"
VECTOR_SIZE = 4096

def run_qdrant_test():
    """Create a simple test collection and perform basic operations."""
    client = QdrantClient(host="localhost", port=6333)
    
    logger.info("Creating test collection")
    
    # Delete if exists
    try:
        collections = client.get_collections()
        if TEST_COLLECTION in [c.name for c in collections.collections]:
            client.delete_collection(TEST_COLLECTION)
            logger.info(f"Deleted existing collection: {TEST_COLLECTION}")
    except Exception as e:
        logger.error(f"Error checking collections: {e}")
    
    # Create collection
    try:
        client.create_collection(
            collection_name=TEST_COLLECTION,
            vectors_config=models.VectorParams(
                size=VECTOR_SIZE,
                distance=models.Distance.DOT
            )
        )
        logger.info(f"Created collection: {TEST_COLLECTION}")
    except Exception as e:
        logger.error(f"Error creating collection: {e}")
        return False
    
    # Create a single test vector (all 1.0 values)
    test_vector = [1.0] * VECTOR_SIZE
    
    # Insert test point
    try:
        client.upsert(
            collection_name=TEST_COLLECTION,
            points=[
                models.PointStruct(
                    id=1,
                    vector=test_vector,
                    payload={"text": "This is a test document"}
                )
            ]
        )
        logger.info("Inserted test point")
    except Exception as e:
        logger.error(f"Error inserting point: {e}")
        return False
    
    # Retrieve the point
    try:
        point = client.retrieve(TEST_COLLECTION, ids=[1])
        if point:
            logger.info(f"Successfully retrieved point with ID 1")
        else:
            logger.error("Could not retrieve point")
            return False
    except Exception as e:
        logger.error(f"Error retrieving point: {e}")
        return False
    
    # Search for the point
    try:
        # Create a similar vector
        search_vector = [0.9] * VECTOR_SIZE
        results = client.search(
            collection_name=TEST_COLLECTION,
            query_vector=search_vector,
            limit=1
        )
        
        if results:
            logger.info(f"Search successful, found point with ID: {results[0].id}")
            return True
        else:
            logger.error("Search returned no results")
            return False
    except Exception as e:
        logger.error(f"Error during search: {e}")
        return False

if __name__ == "__main__":
    success = run_qdrant_test()
    if success:
        print("\n✅ Qdrant is working properly!")
    else:
        print("\n❌ Qdrant has issues that need to be resolved.")