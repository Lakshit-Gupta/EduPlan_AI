#!/usr/bin/env python3
"""
Process improved data for EduPlan AI system.
This script loads the improved JSON data, generates embeddings using NV-Embed,
and stores them in the Qdrant vector database for efficient retrieval.
"""

import sys
import os
import json
import time
from typing import List, Dict, Any, Tuple
from pathlib import Path
import logging

# Add parent directory to path to import modules
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

# Import required modules
from src.models.embedding_model import NVEmbedPipeline
from src.database.qdrant_connector import QdrantConnector
from src.core.config import QDRANT_COLLECTION_NAME, QDRANT_HOST, QDRANT_PORT, QDRANT_VECTOR_SIZE

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_improved_data(data_dir: str = "../../data/processed_improved") -> List[Dict[str, Any]]:
    """
    Load all improved data files from the specified directory.
    
    Args:
        data_dir: Directory containing improved JSON data files
    
    Returns:
        List of dictionaries containing the loaded data
    """
    data_path = Path(os.path.join(os.path.dirname(__file__), data_dir))
    logger.info(f"Loading improved data from {data_path}")
    
    all_data = []
    
    if not data_path.exists():
        logger.error(f"Data directory not found: {data_path}")
        return all_data
    
    for json_file in data_path.glob("*_improved.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Loaded {json_file.name}: {len(data) if isinstance(data, list) else '1'} items")
                all_data.append({
                    "file": json_file.name,
                    "data": data
                })
        except Exception as e:
            logger.error(f"Error loading {json_file}: {e}")
    
    return all_data

def prepare_documents(improved_data: List[Dict[str, Any]]) -> Tuple[List[str], List[Dict[str, Any]]]:
    """
    Extract text and metadata from improved data with optimized chunking.
    
    Args:
        improved_data: List of dictionaries containing improved data
    
    Returns:
        Tuple containing (text_chunks, metadata)
    """
    texts = []
    metadata = []
    
    for file_data in improved_data:
        filename = file_data["file"]
        data = file_data["data"]
        
        # Extract chapter information from filename
        chapter_name = filename.split('_')[0]
        
        # Process based on data format
        if isinstance(data, dict) and "metadata" in data and "sections" in data:
            # New format (complex structure with metadata and sections)
            logger.info(f"Processing {filename} using complex format")
            chapter_metadata = data.get("metadata", {})
            chapter_number = chapter_metadata.get("chapter_number", chapter_name.replace("Chapter_", ""))
            
            # Extract all text content from all sections
            for section_idx, section in enumerate(data.get("sections", [])):
                section_title = section.get("title", "")
                
                # Collect all textual content
                all_content = []
                
                # Add section title
                if section_title:
                    all_content.append(section_title)
                
                # Add all content items
                if "content" in section and isinstance(section["content"], list):
                    all_content.extend(section["content"])
                
                # Add questions if available
                if "questions" in section and isinstance(section["questions"], list):
                    all_content.extend(section["questions"])
                    
                # Add activities if available
                if "activities" in section and isinstance(section["activities"], list):
                    all_content.extend(section["activities"])
                
                # Combine text into chunks of appropriate size (about 500 tokens)
                current_chunk = ""
                chunk_count = 0
                
                for content_item in all_content:
                    if not content_item or not isinstance(content_item, str):
                        continue
                        
                    # If adding this item would make the chunk too large, save current chunk
                    if len(current_chunk) + len(content_item) > 2000:  # ~500 tokens
                        if current_chunk:
                            # Add the current chunk to our texts list
                            texts.append(current_chunk)
                            
                            # Add corresponding metadata
                            meta = {
                                "id": f"{filename}_s{section_idx}_chunk_{chunk_count}",
                                "chapter": f"Chapter {chapter_number}",
                                "source": filename,
                                "type": section.get("type", "section"),
                                "section": section_title,
                                "chunk": chunk_count
                            }
                            metadata.append(meta)
                            
                            # Start a new chunk
                            chunk_count += 1
                            current_chunk = content_item
                        else:
                            # If the item itself is very large, use it as a chunk
                            texts.append(content_item)
                            
                            # Add corresponding metadata
                            meta = {
                                "id": f"{filename}_s{section_idx}_chunk_{chunk_count}",
                                "chapter": f"Chapter {chapter_number}",
                                "source": filename,
                                "type": section.get("type", "section"),
                                "section": section_title,
                                "chunk": chunk_count
                            }
                            metadata.append(meta)
                            chunk_count += 1
                    else:
                        # Add to current chunk with a space
                        if current_chunk:
                            current_chunk += " " + content_item
                        else:
                            current_chunk = content_item
                
                # Don't forget the last chunk
                if current_chunk:
                    texts.append(current_chunk)
                    
                    # Add corresponding metadata
                    meta = {
                        "id": f"{filename}_s{section_idx}_chunk_{chunk_count}",
                        "chapter": f"Chapter {chapter_number}",
                        "source": filename,
                        "type": section.get("type", "section"),
                        "section": section_title,
                        "chunk": chunk_count
                    }
                    metadata.append(meta)
        
        elif isinstance(data, list) and all(isinstance(item, dict) for item in data):
            # Old format (simple list of dictionaries)
            logger.info(f"Processing {filename} using simple format")
            for item in data:
                try:
                    # Get the text content
                    content = item.get("content", "")
                    if not content:
                        continue
                        
                    # Add text to chunks
                    texts.append(content)
                    
                    # Prepare metadata
                    meta = {
                        "id": f"{filename}_item_{len(texts)}",
                        "chapter": item.get("chapter", chapter_name),
                        "source": filename,
                        "type": item.get("type", "unknown"),
                        "section": item.get("section", ""),

                        "subsection": item.get("subsection", ""),
                        "index": item.get("index", 0)
                    }
                    metadata.append(meta)
                except Exception as e:
                    logger.error(f"Error processing item in {filename}: {e}")
        
        else:
            logger.warning(f"Unknown data format for file: {filename}")
    
    logger.info(f"Prepared {len(texts)} documents with metadata")
    return texts, metadata


def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for text chunks using NV-Embed.
    
    Args:
        texts: List of text chunks to embed
    
    Returns:
        List of embedding vectors
    """
    logger.info("Initializing NV-Embed model...")
    embedding_model = NVEmbedPipeline()
    
    logger.info(f"Generating embeddings for {len(texts)} documents...")
    start_time = time.time()
    embeddings = embedding_model.embed_texts(texts)
    elapsed = time.time() - start_time
    
    logger.info(f"Generated {len(embeddings)} embeddings in {elapsed:.2f} seconds")
    
    # Debug: Check the format of embeddings
    if embeddings and len(embeddings) > 0:
        first_emb = embeddings[0]
        logger.info(f"First embedding type: {type(first_emb)}")
        logger.info(f"First embedding length: {len(first_emb)}")
        if hasattr(first_emb, 'tolist') and callable(getattr(first_emb, 'tolist')):
            logger.info("Converting embeddings from numpy/tensor to list format")
            embeddings = [emb.tolist() for emb in embeddings]
    
    return embeddings

def store_in_database(texts, embeddings, metadata, collection_name="science_9_collection"):
    """
    Store documents and embeddings in Qdrant.
    
    Args:
        texts: List of text chunks
        embeddings: List of embedding vectors
        metadata: List of metadata dictionaries
        collection_name: Name of the Qdrant collection
    """
    logger.info(f"Storing data in collection: {collection_name}")
    
    # Always use 4096 for NV-Embed vector size
    vector_size = 4096
    logger.info(f"Using vector size: {vector_size}")
    
    # Create Qdrant connector
    qdrant = QdrantConnector(
        host=QDRANT_HOST,
        port=QDRANT_PORT,
        collection_name=collection_name,
        vector_size=vector_size
    )
    
    # Create collection if it doesn't exist
    qdrant.recreate_collection()
    
    # Prepare documents for insertion
    documents = []
    for i, (text, meta) in enumerate(zip(texts, metadata)):
        # Use numeric ID (required by Qdrant) but save original ID in metadata
        original_id = meta.get("id", f"doc_{i}")
        meta["original_id"] = original_id  # Keep the original ID in metadata
        
        doc = {
            "id": i,  # Use simple numeric ID for Qdrant
            "text": text,
            "metadata": meta
        }
        documents.append(doc)
    
    # Insert documents - don't pass batch_size to avoid parameter conflict
    success = qdrant.insert_documents(documents, embeddings)
    
    if success:
        logger.info(f"Successfully stored {len(documents)} documents in database")
    else:
        logger.error("Failed to store documents in database")
        
    return success

def main():
    """Main processing function"""
    logger.info("Starting improved data processing with NV-Embed")
    
    # Load improved data
    improved_data = load_improved_data()
    if not improved_data:
        logger.error("No improved data found. Exiting.")
        return
    
    # Prepare documents
    texts, metadata = prepare_documents(improved_data)
    if not texts:
        logger.error("No text chunks extracted. Exiting.")
        return
    
    # Generate embeddings
    embeddings = generate_embeddings(texts)
    if not embeddings or len(embeddings) != len(texts):
        logger.error(f"Embedding generation failed. Got {len(embeddings)} embeddings for {len(texts)} texts.")
        return
    
    # Store in database - fix the argument order
    success = store_in_database(texts, embeddings, metadata)
    
    if success:
        logger.info(f"✅ Processing completed successfully!")
        logger.info(f"   Processed {len(texts)} documents across {len(improved_data)} files")
    else:
        logger.error("❌ Processing failed.")

if __name__ == "__main__":
    main()
