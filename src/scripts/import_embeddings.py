#!/usr/bin/env python3
"""
Import embeddings from an exported file into Qdrant.
This allows using pre-generated embeddings without having to regenerate them.
"""
import os
import pickle
import logging
from typing import Union, Optional
from pathlib import Path

from qdrant_client import QdrantClient
from src.core.config import QDRANT_HOST, QDRANT_PORT

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def import_collection(
    import_file: Union[str, Path], 
    collection_name: Optional[str] = None,
    replace_existing: bool = True
) -> bool:
    """
    Import a collection from an exported file into Qdrant.
    
    Args:
        import_file: Path to the exported collection file
        collection_name: Optional name for the imported collection (default: use original name)
        replace_existing: Whether to replace existing collection with same name
        
    Returns:
        True if import was successful
    """
    logger.info(f"Importing collection from {import_file}")
    
    # Load the export file
    with open(import_file, "rb") as f:
        export_data = pickle.load(f)
    
    original_name = export_data["collection_name"]
    vector_size = export_data["vector_size"]
    points = export_data["points"]
    count = export_data["count"]
    
    # Use original name if not specified
    if collection_name is None:
        collection_name = original_name
    
    logger.info(f"Importing collection '{original_name}' to '{collection_name}'")
    logger.info(f"Vector size: {vector_size}, Points: {count}")
    
    # Connect to Qdrant
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    
    try:
        # Check if collection exists
        collections = client.get_collections()
        collection_names = [c.name for c in collections.collections]
        
        if collection_name in collection_names:
            if replace_existing:
                logger.warning(f"Collection '{collection_name}' already exists. Recreating...")
                client.delete_collection(collection_name)
            else:
                logger.error(f"Collection '{collection_name}' already exists and replace_existing=False")
                return False
        
        # Create collection
        client.create_collection(
            collection_name=collection_name,
            vectors_config={
                "size": vector_size,
                "distance": "Cosine"
            }
        )
        
        # Insert points in batches
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i+batch_size]
            
            # Prepare points for insertion
            upsert_points = []
            for p in batch:
                upsert_points.append({
                    "id": p["id"],
                    "vector": p["vector"],
                    "payload": p["payload"]
                })
            
            # Insert batch
            client.upsert(
                collection_name=collection_name,
                points=upsert_points
            )
            
            logger.info(f"Inserted {min(i+batch_size, len(points))}/{len(points)} points")
        
        logger.info(f"Successfully imported {len(points)} points to '{collection_name}'")
        return True
    
    except Exception as e:
        logger.error(f"Error importing collection: {e}")
        raise

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python import_embeddings.py <path_to_export_file> [collection_name]")
        sys.exit(1)
    
    export_file = sys.argv[1]
    collection_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = import_collection(export_file, collection_name)
    
    if success:
        logger.info("✅ Import completed successfully!")
    else:
        logger.error("❌ Import failed.")
        sys.exit(1)