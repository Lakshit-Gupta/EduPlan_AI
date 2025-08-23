import os
import sys
from typing import List, Dict, Any, Tuple
import glob
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import config
from common import utils
from common.embedding.embeddings import DocumentEmbeddings
from common.database.qdrant_connector import QdrantDB

class DocumentIngestionPipeline:
    """
    Pipeline for processing and ingesting documents into the vector database
    """
    
    def __init__(self):
        """Initialize the pipeline components"""
        self.embedder = DocumentEmbeddings()
        self.db = QdrantDB()
        
        # Ensure the collection exists
        self.db.create_collection()
    
    def ingest_file(self, file_path: str) -> Tuple[List[str], Dict[str, Any]]:
        """
        Ingest a single file into the database
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Tuple of (document_ids, metadata)
        """
        # Process document
        chunks, metadata = utils.process_document(file_path)
        
        # Generate embeddings
        embeddings = self.embedder.embed_texts(chunks)
        
        # Create metadata for each chunk
        chunk_metadata = [metadata.copy() for _ in chunks]
        
        # Store in database
        doc_ids = self.db.insert_documents(embeddings, chunks, chunk_metadata)
        
        return doc_ids, metadata
    
    def ingest_directory(self, directory_path: str, file_extension: str = None) -> List[Dict[str, Any]]:
        """
        Ingest all documents in a directory
        
        Args:
            directory_path: Path to directory with documents
            file_extension: Optional file extension filter
            
        Returns:
            List of ingestion results with file info and IDs
        """
        # Get file paths
        if file_extension:
            file_paths = glob.glob(os.path.join(directory_path, f"*.{file_extension}"))
        else:
            extensions = config.ALLOWED_EXTENSIONS
            file_paths = []
            for ext in extensions:
                file_paths.extend(glob.glob(os.path.join(directory_path, f"*.{ext}")))
        
        results = []
        
        # Process each file
        for file_path in file_paths:
            try:
                doc_ids, metadata = self.ingest_file(file_path)
                
                # Add to results
                results.append({
                    "file": os.path.basename(file_path),
                    "class": metadata.get("class", "unknown"),
                    "subject": metadata.get("subject", "unknown"),
                    "chunks": len(doc_ids),
                    "status": "success",
                    "first_id": doc_ids[0] if doc_ids else None
                })
                
                print(f"Ingested: {file_path} - {len(doc_ids)} chunks")
                
            except Exception as e:
                print(f"Error ingesting {file_path}: {e}")
                results.append({
                    "file": os.path.basename(file_path),
                    "status": "error",
                    "error": str(e)
                })
        
        return results
