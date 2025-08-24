#!/usr/bin/env python3
"""
Query embeddings from the Qdrant database.
This script allows you to search for similar documents using semantic queries.
"""

import sys
import os
import numpy as np
from typing import List, Dict, Any

# Add parent directory to path to import modules
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from src.models.embedding_model import NVEmbedPipeline
from src.database.qdrant_connector import QdrantConnector
from qdrant_client import QdrantClient

def search(query: str, collection_name: str = "science_9_collection", top_k: int = 3):
    """
    Search for documents similar to the query.
    
    Args:
        query: Search query text
        collection_name: Name of the collection to search
        top_k: Number of results to return
    """
    print(f"🔍 Searching for: '{query}'")
    
    # Create embedding model
    embedding_model = NVEmbedPipeline()
    
    # Generate query embedding
    query_embedding = embedding_model.embed_query(query)
    
    # Create Qdrant connector
    qdrant = QdrantConnector(
        host="localhost",
        port=6333,
        collection_name=collection_name
    )
    
    # Search for similar documents
    results = qdrant.search_documents(query_embedding, top_k=top_k)
    
    # Display results
    print(f"\n📊 Found {len(results)} results:")
    
    for i, result in enumerate(results):
        print(f"\n{i+1}. Score: {result['score']:.4f}")
        print(f"   Chapter: {result['metadata'].get('chapter', 'Unknown')}")
        print(f"   Section: {result['metadata'].get('section', 'Unknown')}")
        
        # Truncate text for display
        text = result['text']
        if len(text) > 200:
            text = text[:200] + "..."
        
        print(f"   Text: {text}")
    
    return results

def get_embeddings(doc_id: int = None, collection_name: str = "science_9_collection"):
    """
    Get embeddings from Qdrant by document ID.
    
    Args:
        doc_id: ID of the document to fetch (if None, returns first document)
        collection_name: Name of the collection
        
    Returns:
        The embedding vector
    """
    # Connect directly to Qdrant
    client = QdrantClient(host="localhost", port=6333)
    
    try:
        if doc_id is not None:
            # Get a specific document by ID
            points = client.retrieve(
                collection_name=collection_name,
                ids=[doc_id],
                with_vectors=True,
                with_payload=True
            )
            
            if not points:
                print(f"❌ Document with ID {doc_id} not found")
                return None
                
            point = points[0]
        else:
            # Get the first document if no ID specified
            points, _ = client.scroll(
                collection_name=collection_name,
                limit=1,
                with_vectors=True,
                with_payload=True
            )
            
            if not points:
                print("❌ No documents found in collection")
                return None
                
            point = points[0]
        
        # Extract vector and payload
        vector = point.vector
        payload = point.payload
        
        # Print vector information
        print(f"\n📊 Embedding for document ID: {point.id}")
        print(f"Vector dimension: {len(vector)}")
        print(f"Text preview: {payload.get('text', '')[:100]}...")
        
        # Print vector statistics
        vector_array = np.array(vector)
        print(f"\nVector statistics:")
        print(f"  Mean: {vector_array.mean():.6f}")
        print(f"  Min: {vector_array.min():.6f}")
        print(f"  Max: {vector_array.max():.6f}")
        print(f"  Standard deviation: {vector_array.std():.6f}")
        
        # Print first few and last few elements
        preview_size = 5
        print(f"\nFirst {preview_size} elements:")
        for i in range(min(preview_size, len(vector))):
            print(f"  [{i}]: {vector[i]:.6f}")
            
        print(f"\nLast {preview_size} elements:")
        for i in range(max(0, len(vector) - preview_size), len(vector)):
            print(f"  [{i}]: {vector[i]:.6f}")
        
        # Ask if user wants to see the full vector
        if input("\nDo you want to see the complete vector? (y/n): ").lower() == 'y':
            print("\nComplete vector:")
            for i, value in enumerate(vector):
                print(f"  [{i}]: {value:.6f}")
        
        return vector
        
    except Exception as e:
        print(f"❌ Error retrieving embedding: {e}")
        return None

def list_document_ids(collection_name: str = "science_9_collection", limit: int = 10):
    """
    List document IDs in the collection.
    
    Args:
        collection_name: Name of the collection
        limit: Maximum number of documents to list
    """
    # Connect directly to Qdrant
    client = QdrantClient(host="localhost", port=6333)
    
    try:
        # First check if the collection exists
        collections = client.get_collections()
        collection_names = [c.name for c in collections.collections]
        
        if collection_name not in collection_names:
            print(f"❌ Collection '{collection_name}' not found")
            print(f"Available collections: {collection_names}")
            return
        
        print(f"🔍 Retrieving documents from collection '{collection_name}'...")
        
        try:
            # Try a simpler approach first - just get the collection info
            collection_info = client.get_collection(collection_name)
            print(f"Collection exists with config: {collection_info.config.params}")
            
            # Try to count the documents
            count_result = client.count(collection_name)
            print(f"Collection contains {count_result.count} points")
            
            # Alternative method to get points - use search with a dummy vector
            # This avoids the scroll API which might be causing issues
            if count_result.count > 0:
                # Create a dummy vector of the right size
                vector_size = collection_info.config.params.vectors.size
                dummy_vector = [0.0] * vector_size
                
                # Search with this dummy vector (will return points sorted by distance)
                search_results = client.search(
                    collection_name=collection_name,
                    query_vector=dummy_vector,
                    limit=limit,
                    with_payload=True
                )
                
                print(f"\n📋 Documents in collection '{collection_name}':")
                
                for result in search_results:
                    point_id = result.id
                    payload = result.payload
                    metadata = payload.get("metadata", {})
                    text = payload.get("text", "")
                    
                    # Truncate text for display
                    text_preview = text[:50] + "..." if len(text) > 50 else text
                    
                    print(f"ID: {point_id}")
                    print(f"  Chapter: {metadata.get('chapter', 'Unknown')}")
                    print(f"  Section: {metadata.get('section', 'Unknown')}")
                    print(f"  Text: {text_preview}")
                    print()
            else:
                print("Collection is empty")
            
        except Exception as inner_e:
            print(f"❌ Error accessing collection: {inner_e}")
    
    except Exception as e:
        print(f"❌ Error listing documents: {e}")
        print("Try restarting the Qdrant server if the error persists.")

if __name__ == "__main__":
    print("\n🔍 QDRANT EMBEDDINGS EXPLORER")
    print("="*50)
    print("1. Search by query")
    print("2. Get embedding by document ID")
    print("3. List document IDs")
    print("4. Exit")
    
    choice = input("\nEnter choice (1-4): ")
    
    if choice == "1":
        query = input("Enter your search query: ")
        search(query)
    elif choice == "2":
        try:
            doc_id = int(input("Enter document ID (or press Enter for first document): ") or "0")
            get_embeddings(doc_id)
        except ValueError:
            print("Invalid ID. Using the first document.")
            get_embeddings()
    elif choice == "3":
        try:
            limit = int(input("How many documents to list? (default: 10): ") or "10")
            list_document_ids(limit=limit)
        except ValueError:
            print("Invalid input. Using default limit of 10.")
            list_document_ids()
    elif choice == "4":
        print("Goodbye!")
    else:
        print("Invalid choice.")