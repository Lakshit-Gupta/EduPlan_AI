#!/usr/bin/env python3
"""
Fix existing science_9_collection with correct settings.
"""

from qdrant_client import QdrantClient, models
import logging
from src.models.embedding_model import NVEmbedPipeline
from typing import List, Dict, Any, Tuple
import json
from pathlib import Path
import time
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Collection settings
COLLECTION_NAME = "science_9_collection"
VECTOR_SIZE = 4096

def load_improved_data(data_dir: str = "data/improved") -> List[Dict[str, Any]]:
    """Load the improved data from JSON files."""
    data_path = Path(data_dir)
    improved_data = []
    
    if not data_path.exists():
        logger.error(f"Data directory not found: {data_path}")
        return []
    
    for json_file in data_path.glob("*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data:
                    data["_filename"] = json_file.name
                    improved_data.append(data)
                    logger.info(f"Loaded {json_file.name}")
        except Exception as e:
            logger.error(f"Error loading {json_file}: {e}")
    
    logger.info(f"Loaded {len(improved_data)} improved data files")
    return improved_data

def prepare_documents(data: List[Dict[str, Any]]) -> Tuple[List[str], List[Dict]]:
    """Prepare text chunks and metadata from the improved data."""
    texts = []
    metadata = []
    
    for i, doc in enumerate(data):
        filename = doc.get("_filename", f"doc_{i}")
        chapter = doc.get("chapter", "Unknown")
        
        for s_idx, section in enumerate(doc.get("sections", [])):
            section_title = section.get("title", f"Section {s_idx}")
            section_content = section.get("content", "")
            
            chunk_id = f"{filename}_s{s_idx}"
            
            meta = {
                "chapter": chapter,
                "section": section_title,
                "source": filename,
                "original_id": chunk_id
            }
            
            texts.append(section_content)
            metadata.append(meta)
    
    logger.info(f"Prepared {len(texts)} text chunks")
    return texts, metadata

def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate embeddings using the NVEmbedPipeline."""
    model = NVEmbedPipeline()
    
    start_time = time.time()
    embeddings = model.embed_texts(texts)
    duration = time.time() - start_time
    
    logger.info(f"Generated {len(embeddings)} embeddings in {duration:.2f} seconds")
    
    # Verify embeddings
    if embeddings:
        logger.info(f"First embedding length: {len(embeddings[0])}")
    
    return embeddings

def fix_collection():
    """Fix the science_9_collection."""
    client = QdrantClient(host="localhost", port=6333)
    
    # 1. Check if collection exists and delete it
    collections = client.get_collections()
    if COLLECTION_NAME in [c.name for c in collections.collections]:
        logger.info(f"Deleting existing collection: {COLLECTION_NAME}")
        client.delete_collection(COLLECTION_NAME)
    
    # 2. Create new collection with DOT product (more reliable than COSINE)
    logger.info(f"Creating new collection: {COLLECTION_NAME}")
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=VECTOR_SIZE,
            distance=models.Distance.DOT  # Use DOT product which was successful in test
        )
    )
    
    # 3. Load and prepare data
    improved_data = load_improved_data()
    if not improved_data:
        logger.error("No data found")
        return False
    
    texts, metadata = prepare_documents(improved_data)
    
    # 4. Generate embeddings
    embeddings = generate_embeddings(texts)
    
    # 5. Insert points in small batches
    batch_size = 5
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        batch_embeddings = embeddings[i:i+batch_size]
        batch_metadata = metadata[i:i+batch_size]
        
        points = []
        for j, (text, embedding, meta) in enumerate(zip(batch_texts, batch_embeddings, batch_metadata)):
            # Use simple integer IDs
            point_id = i + j
            
            # Check embedding dimensions
            if len(embedding) != VECTOR_SIZE:
                logger.warning(f"Embedding {point_id} has wrong size: {len(embedding)}")
                continue
            
            # Ensure vector values are valid floats
            valid_embedding = True
            for val in embedding:
                if not np.isfinite(val):  # Check for NaN or Inf
                    valid_embedding = False
                    break
            
            if not valid_embedding:
                logger.warning(f"Embedding {point_id} contains invalid values")
                continue
                
            point = models.PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "text": text,
                    "metadata": meta
                }
            )
            points.append(point)
        
        # Insert batch
        if points:
            try:
                client.upsert(
                    collection_name=COLLECTION_NAME,
                    points=points
                )
                logger.info(f"Inserted batch {i//batch_size + 1}, {len(points)} points")
            except Exception as e:
                logger.error(f"Error inserting batch: {e}")
    
    # 6. Verify collection
    try:
        count = client.count(COLLECTION_NAME).count
        logger.info(f"Collection contains {count} points")
        
        # Test search with a random vector
        random_vector = np.random.rand(VECTOR_SIZE).tolist()
        results = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=random_vector,
            limit=1
        )
        
        if results:
            logger.info(f"Search successful, found point with ID: {results[0].id}")
            return True
        else:
            logger.error("Search returned no results")
            return False
    except Exception as e:
        logger.error(f"Error verifying collection: {e}")
        return False

if __name__ == "__main__":
    success = fix_collection()
    if success:
        print("\n✅ Collection fixed successfully!")
    else:
        print("\n❌ Failed to fix collection.")