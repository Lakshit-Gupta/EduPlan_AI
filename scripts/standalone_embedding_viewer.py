#!/usr/bin/env python3
"""
Standalone embedding viewer - doesn't require project imports.
"""

import sys
import os
import json
from pathlib import Path
import numpy as np
import logging
from transformers import AutoModel, AutoTokenizer
import torch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StandaloneEmbedder:
    """Standalone embedding model that doesn't rely on project imports."""
    
    def __init__(self, model_name="NVIDIA/NV-Embed-QA"):
        """Initialize embedding model."""
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.vector_size = 4096  # NV-Embed dimension
        
        print(f"Loading model {model_name} on {self.device}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        print("Model loaded successfully")
    
    def embed_query(self, text):
        """Generate embedding for a single text."""
        # Tokenize
        inputs = self.tokenizer(
            text, 
            padding=True, 
            truncation=True, 
            max_length=512,
            return_tensors="pt"
        ).to(self.device)
        
        # Generate embedding
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # Extract embedding
        if isinstance(outputs, dict) and "sentence_embeddings" in outputs:
            embedding = outputs["sentence_embeddings"][0].cpu().numpy()
        else:
            # Get tokens and apply mean pooling
            tokens = outputs.last_hidden_state
            mask = inputs["attention_mask"]
            
            # Apply mask
            masked_tokens = tokens * mask.unsqueeze(-1)
            # Sum and divide by non-zero elements
            summed = torch.sum(masked_tokens, dim=1)
            counts = torch.sum(mask, dim=1).unsqueeze(-1)
            embedding = (summed / counts)[0].cpu().numpy()
        
        return embedding.tolist()

def load_document(file_path):
    """Load a document from JSON file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading file {file_path}: {e}")
        return None

def extract_text_chunks(doc):
    """Extract text chunks from document."""
    chunks = []
    metadata = []
    
    chapter = doc.get("chapter", "Unknown")
    filename = doc.get("_filename", "")
    
    for s_idx, section in enumerate(doc.get("sections", [])):
        section_title = section.get("title", f"Section {s_idx}")
        section_content = section.get("content", "")
        
        chunk_id = f"{filename}_s{s_idx}" if filename else f"chunk_{s_idx}"
        
        chunks.append(section_content)
        metadata.append({
            "id": chunk_id,
            "chapter": chapter,
            "section": section_title
        })
    
    return chunks, metadata

def view_embeddings(file_path=None):
    """Generate and view embeddings directly from a document."""
    # Find document file if not specified
    if file_path is None:
        data_dir = Path("data/improved")
        if data_dir.exists():
            json_files = list(data_dir.glob("*.json"))
            if json_files:
                file_path = str(json_files[0])
                print(f"Using first available file: {file_path}")
            else:
                print("No JSON files found in data/improved")
                return None, None, None
        else:
            print(f"Directory not found: {data_dir}")
            return None, None, None
    
    # Load document
    doc = load_document(file_path)
    if not doc:
        return None, None, None
    
    # Extract text chunks
    chunks, chunk_metadata = extract_text_chunks(doc)
    if not chunks:
        print("No text chunks found in document")
        return None, None, None
    
    print(f"Extracted {len(chunks)} text chunks from document")
    
    # Initialize embedding model
    try:
        model = StandaloneEmbedder()
    except Exception as e:
        print(f"Error loading embedding model: {e}")
        print("You may need to install required packages:")
        print("pip install torch transformers")
        return None, None, None
    
    # Generate embeddings (one at a time to avoid memory issues)
    embeddings = []
    for i, chunk in enumerate(chunks):
        print(f"Generating embedding for chunk {i+1}/{len(chunks)}...")
        embedding = model.embed_query(chunk)
        embeddings.append(embedding)
        
        # Show embedding info
        print(f"Chunk {i+1}: {chunk_metadata[i]['section']}")
        print(f"  Vector dimension: {len(embedding)}")
        print(f"  First 5 values: {embedding[:5]}")
        print(f"  Mean: {np.mean(embedding):.6f}")
        print(f"  Min: {np.min(embedding):.6f}")
        print(f"  Max: {np.max(embedding):.6f}")
        print()
    
    # Save embeddings to file
    output_dir = Path("embeddings_output")
    output_dir.mkdir(exist_ok=True)
    
    # Get base filename
    base_name = Path(file_path).stem
    output_path = output_dir / f"{base_name}_embeddings.json"
    
    # Save in a readable format
    output_data = {
        "source_file": file_path,
        "chunk_count": len(chunks),
        "vector_size": len(embeddings[0]) if embeddings else 0,
        "chunks": [
            {
                "metadata": meta,
                "text": text[:100] + "..." if len(text) > 100 else text,
                "embedding_preview": emb[:10],  # Just first 10 values
                "embedding_stats": {
                    "mean": float(np.mean(emb)),
                    "min": float(np.min(emb)),
                    "max": float(np.max(emb))
                }
            }
            for meta, text, emb in zip(chunk_metadata, chunks, embeddings)
        ]
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n✅ Embeddings saved to: {output_path}")
    
    # Also save the full embeddings in NumPy format for efficiency
    np_output_path = output_dir / f"{base_name}_embeddings.npy"
    np.save(np_output_path, np.array(embeddings))
    print(f"✅ Full embeddings saved to: {np_output_path}")
    
    return embeddings, chunks, chunk_metadata

def compare_chunks(chunks, embeddings, metadata):
    """Compare similarity between chunks."""
    # Print available chunks
    print("\nAvailable chunks:")
    for i, meta in enumerate(metadata):
        print(f"{i}: {meta['section']}")
    
    # Get indices to compare
    try:
        idx1 = int(input("\nEnter first chunk index: "))
        idx2 = int(input("Enter second chunk index: "))
        
        if 0 <= idx1 < len(chunks) and 0 <= idx2 < len(chunks):
            # Calculate cosine similarity
            emb1 = np.array(embeddings[idx1])
            emb2 = np.array(embeddings[idx2])
            
            # Normalize vectors
            emb1_norm = emb1 / np.linalg.norm(emb1)
            emb2_norm = emb2 / np.linalg.norm(emb2)
            
            # Calculate similarity
            similarity = np.dot(emb1_norm, emb2_norm)
            
            print(f"\nSimilarity between chunks: {similarity:.4f}")
            print(f"Chunk 1: {metadata[idx1]['section']}")
            print(f"Chunk 2: {metadata[idx2]['section']}")
        else:
            print("Invalid indices")
    except Exception as e:
        print(f"Error: {e}")

def search_with_query(query, embeddings, chunks, metadata):
    """Search chunks using a query."""
    if not embeddings:
        print("No embeddings available")
        return
    
    # Get query embedding
    try:
        model = StandaloneEmbedder()
        query_embedding = np.array(model.embed_query(query))
    except Exception as e:
        print(f"Error generating query embedding: {e}")
        return
    
    # Normalize query vector
    query_norm = query_embedding / np.linalg.norm(query_embedding)
    
    # Calculate similarities
    similarities = []
    for i, emb in enumerate(embeddings):
        emb_array = np.array(emb)
        emb_norm = emb_array / np.linalg.norm(emb_array)
        similarity = np.dot(query_norm, emb_norm)
        similarities.append((i, similarity))
    
    # Sort by similarity (highest first)
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    # Print results
    print(f"\n🔍 Search results for: '{query}'")
    print("=" * 50)
    
    for idx, score in similarities[:3]:  # Top 3 results
        print(f"Score: {score:.4f}")
        print(f"Chapter: {metadata[idx]['chapter']}")
        print(f"Section: {metadata[idx]['section']}")
        
        # Show text preview
        text = chunks[idx]
        preview = text[:150] + "..." if len(text) > 150 else text
        print(f"Text: {preview}")
        print("-" * 50)

if __name__ == "__main__":
    # Get file path from arguments or prompt
    file_path = None
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    
    # Run the viewer
    embeddings, chunks, metadata = view_embeddings(file_path)
    
    # Allow user to search with a query
    if embeddings:
        print("\nWould you like to search using a query? (y/n)")
        if input().lower() == "y":
            query = input("Enter your search query: ")
            search_with_query(query, embeddings, chunks, metadata)