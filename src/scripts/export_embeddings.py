#!/usr/bin/env python3
"""
Export embeddings from Qdrant to a file for sharing.
"""

import os
import json
import pickle
from datetime import datetime
from qdrant_client import QdrantClient

def export_embeddings(collection_name="science_9_collection", 
                     export_dir="exports",
                     include_vectors=True):
    """Export embeddings from Qdrant to a file."""
    # Create export directory if it doesn't exist
    os.makedirs(export_dir, exist_ok=True)
    
    # Connect to Qdrant
    client = QdrantClient(host="localhost", port=6333)
    
    # Timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Filename based on whether vectors are included
    if include_vectors:
        filename = f"{collection_name}_{timestamp}_with_vectors.pkl"
    else:
        filename = f"{collection_name}_{timestamp}_metadata_only.json"
    
    export_path = os.path.join(export_dir, filename)
    
    # Get all points from collection
    points = []
    offset = None
    batch_size = 100
    
    print(f"Exporting collection '{collection_name}'...")
    
    while True:
        records, next_offset = client.scroll(
            collection_name=collection_name,
            limit=batch_size,
            offset=offset,
            with_vectors=include_vectors,
            with_payload=True
        )
        
        if not records:
            break
        
        for record in records:
            point = {
                "id": record.id,
                "payload": record.payload
            }
            
            if include_vectors and record.vector:
                point["vector"] = record.vector
                
            points.append(point)
        
        print(f"Fetched {len(points)} points so far...")
        
        if next_offset is None:
            break
            
        offset = next_offset
    
    # Export data
    export_data = {
        "collection_name": collection_name,
        "timestamp": timestamp,
        "count": len(points),
        "points": points
    }
    
    # Save to file
    if include_vectors:
        # Use pickle for vector data (more efficient)
        with open(export_path, "wb") as f:
            pickle.dump(export_data, f)
    else:
        # Use JSON for metadata only (more portable)
        with open(export_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2)
    
    print(f"✅ Exported {len(points)} points to {export_path}")
    return export_path

if __name__ == "__main__":
    import sys
    
    # Default values
    collection = "science_9_collection"
    vectors = True
    
    # Parse arguments
    if len(sys.argv) > 1:
        collection = sys.argv[1]
        
    if len(sys.argv) > 2:
        vectors = sys.argv[2].lower() in ("true", "t", "yes", "y", "1")
    
    export_path = export_embeddings(collection, include_vectors=vectors)
    print(f"Export complete: {export_path}")