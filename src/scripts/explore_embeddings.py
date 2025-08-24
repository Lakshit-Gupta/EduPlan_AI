#!/usr/bin/env python3
"""
Explore embeddings stored in Qdrant database.
This script allows you to view, search, and analyze stored embeddings.
"""

import sys
import os
import json
from typing import List, Dict, Any, Optional
import logging
from pprint import pprint
from pathlib import Path
from tabulate import tabulate  # pip install tabulate

# Add parent directory to path to import modules
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from src.models.embedding_model import NVEmbedPipeline
from src.database.qdrant_connector import QdrantConnector
from src.core.config import QDRANT_HOST, QDRANT_PORT

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_collection_info(collection_name: str = "science_9_collection") -> Dict[str, Any]:
    """
    Get information about a Qdrant collection.
    
    Args:
        collection_name: Name of the collection to query
        
    Returns:
        Dictionary with collection information
    """
    from qdrant_client import QdrantClient
    
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    
    try:
        # Check if collection exists
        collections = client.get_collections()
        collection_names = [c.name for c in collections.collections]
        
        if collection_name not in collection_names:
            logger.error(f"Collection '{collection_name}' not found.")
            return {}
        
        # Get collection info
        collection_info = client.get_collection(collection_name)
        
        # Get collection size
        collection_size = client.count(collection_name).count
        
        # Get sample points
        samples, _ = client.scroll(
            collection_name=collection_name,
            limit=5,
            with_vectors=True,
            with_payload=True
        )
        
        info = {
            "name": collection_name,
            "vector_size": collection_info.config.params.vectors.size,
            "distance": collection_info.config.params.vectors.distance,
            "count": collection_size,
            "samples": [
                {
                    "id": p.id,
                    "vector_len": len(p.vector) if p.vector else 0,
                    "payload_keys": list(p.payload.keys()) if p.payload else []
                }
                for p in samples
            ]
        }
        
        return info
    
    except Exception as e:
        logger.error(f"Error getting collection info: {e}")
        return {}

def list_documents(collection_name: str = "science_9_collection", limit: int = 10) -> List[Dict[str, Any]]:
    """
    List documents in the collection.
    
    Args:
        collection_name: Name of the collection to query
        limit: Maximum number of documents to return
        
    Returns:
        List of document dictionaries
    """
    from qdrant_client import QdrantClient
    
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    
    try:
        # Get documents
        records, _ = client.scroll(
            collection_name=collection_name,
            limit=limit,
            with_payload=True
        )
        
        # Format documents
        documents = []
        for record in records:
            if record.payload:
                # Extract text and metadata
                text = record.payload.get("text", "")
                metadata = record.payload.get("metadata", {})
                
                # Truncate text for display
                truncated_text = text[:100] + "..." if len(text) > 100 else text
                
                document = {
                    "id": record.id,
                    "text": truncated_text,
                    "metadata": metadata
                }
                documents.append(document)
        
        return documents
    
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        return []

def semantic_search(query: str, collection_name: str = "science_9_collection", limit: int = 5) -> List[Dict[str, Any]]:
    """
    Perform semantic search on the collection.
    
    Args:
        query: Search query text
        collection_name: Name of the collection to search
        limit: Maximum number of results to return
        
    Returns:
        List of search results
    """
    # Load embedding model
    embedding_model = NVEmbedPipeline()
    
    # Generate query embedding
    query_embedding = embedding_model.embed_query(query)
    
    # Search Qdrant
    from qdrant_client import QdrantClient
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    
    try:
        # Perform search
        search_results = client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=limit,
            with_payload=True
        )
        
        # Format results
        results = []
        for hit in search_results:
            text = hit.payload.get("text", "")
            metadata = hit.payload.get("metadata", {})
            
            # Truncate text for display
            truncated_text = text[:150] + "..." if len(text) > 150 else text
            
            result = {
                "score": hit.score,
                "id": hit.id,
                "text": truncated_text,
                "metadata": metadata
            }
            results.append(result)
        
        return results
    
    except Exception as e:
        logger.error(f"Error searching: {e}")
        return []

def export_collection(collection_name: str = "science_9_collection", output_path: Optional[str] = None) -> str:
    """
    Export collection data to a JSON file.
    
    Args:
        collection_name: Name of the collection to export
        output_path: Optional output file path
        
    Returns:
        Path to the exported file
    """
    from qdrant_client import QdrantClient
    
    if output_path is None:
        output_path = f"{collection_name}_export.json"
    
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    
    try:
        # Get all documents
        all_records = []
        offset = None
        batch_size = 100
        
        while True:
            batch, next_offset = client.scroll(
                collection_name=collection_name,
                limit=batch_size,
                offset=offset,
                with_payload=True
            )
            
            if not batch:
                break
            
            for record in batch:
                all_records.append({
                    "id": record.id,
                    "payload": record.payload
                })
            
            if next_offset is None:
                break
            
            offset = next_offset
        
        # Export to file
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({
                "collection": collection_name,
                "count": len(all_records),
                "records": all_records
            }, f, indent=2)
        
        logger.info(f"Exported {len(all_records)} records to {output_path}")
        return output_path
    
    except Exception as e:
        logger.error(f"Error exporting collection: {e}")
        return ""

def show_menu():
    """Display the interactive menu."""
    print("\n" + "="*60)
    print("📊 QDRANT EMBEDDINGS EXPLORER")
    print("="*60)
    print("1. Show collection information")
    print("2. List documents (first 10)")
    print("3. Perform semantic search")
    print("4. Export collection to JSON")
    print("0. Exit")
    print("="*60)

def main():
    """Main interactive function."""
    collection_name = "science_9_collection"
    
    while True:
        show_menu()
        choice = input("Enter your choice (0-4): ")
        
        if choice == "0":
            print("Goodbye!")
            break
        
        elif choice == "1":
            print("\n📊 COLLECTION INFORMATION")
            info = get_collection_info(collection_name)
            if info:
                print(f"Name: {info['name']}")
                print(f"Vector size: {info['vector_size']}")
                print(f"Distance metric: {info['distance']}")
                print(f"Document count: {info['count']}")
                print("\nSample documents:")
                
                for i, sample in enumerate(info['samples']):
                    print(f"  {i+1}. ID: {sample['id']}, Vector length: {sample['vector_len']}")
                    print(f"     Payload keys: {', '.join(sample['payload_keys'])}")
            else:
                print("No collection information available.")
        
        elif choice == "2":
            print("\n📄 DOCUMENT LIST")
            documents = list_documents(collection_name)
            
            if documents:
                table_data = []
                for doc in documents:
                    table_data.append([
                        doc["id"],
                        doc["metadata"].get("chapter", ""),
                        doc["metadata"].get("section", ""),
                        doc["text"]
                    ])
                
                print(tabulate(
                    table_data,
                    headers=["ID", "Chapter", "Section", "Text Preview"],
                    tablefmt="grid"
                ))
            else:
                print("No documents found.")
        
        elif choice == "3":
            query = input("\n🔍 Enter your search query: ")
            if query:
                print(f"\nSearching for: '{query}'")
                results = semantic_search(query, collection_name)
                
                if results:
                    print("\nSearch results:")
                    table_data = []
                    
                    for i, result in enumerate(results):
                        table_data.append([
                            f"{i+1}.",
                            f"{result['score']:.4f}",
                            result["metadata"].get("chapter", ""),
                            result["metadata"].get("section", ""),
                            result["text"]
                        ])
                    
                    print(tabulate(
                        table_data,
                        headers=["#", "Score", "Chapter", "Section", "Text Preview"],
                        tablefmt="grid"
                    ))
                else:
                    print("No results found.")
        
        elif choice == "4":
            output_path = input("\n💾 Enter output file path (or press Enter for default): ")
            if not output_path:
                output_path = None
            
            export_path = export_collection(collection_name, output_path)
            if export_path:
                print(f"Collection exported to: {export_path}")
        
        else:
            print("Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()