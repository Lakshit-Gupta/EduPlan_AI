#!/usr/bin/env python3
"""
Run the improved EduPlan AI pipeline.
This script demonstrates the full pipeline of generating a lesson plan
using the improved data and embeddings.
"""

import sys
import os
import json
import time
from typing import List, Dict, Any
import logging
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import required modules
from src.models.embedding_model import NVEmbedPipeline
from src.database.qdrant_connector import QdrantConnector
from src.core.config import (
    QDRANT_HOST, 
    QDRANT_PORT, 
    QDRANT_COLLECTION_NAME,
    LESSON_PLANS_DIR
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LessonPlanGenerator:
    """Generate lesson plans using vector search."""
    
    def __init__(self):
        """Initialize the lesson plan generator."""
        # Initialize embedding model
        self.embedder = NVEmbedPipeline()
        
        # Initialize database connector
        self.db = QdrantConnector(
            host=QDRANT_HOST,
            port=QDRANT_PORT,
            collection_name=QDRANT_COLLECTION_NAME,
            vector_size=4096
        )
        
    def _build_filter(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build a filter for the vector search.
        
        Args:
            filters: Dictionary of filters to apply
            
        Returns:
            Filter dictionary for Qdrant
        """
        if not filters:
            return None
            
        must_conditions = []
        
        for key, value in filters.items():
            if key in ["chapter", "subject"]:
                # Handle metadata filters
                must_conditions.append({
                    "key": f"metadata.{key}",
                    "match": {"value": value}
                })
                
        if must_conditions:
            return {"must": must_conditions}
        else:
            return None
            
    def search(self, query: str, filters: Dict[str, Any] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant documents.
        
        Args:
            query: Query text
            filters: Optional filters to apply
            limit: Maximum number of results to return
            
        Returns:
            List of relevant documents
        """
        # Generate query embedding
        query_embedding = self.embedder.embed_query(query)
        
        # Build filter
        qdrant_filter = self._build_filter(filters)
        
        # Search for relevant documents
        results = self.db.search_documents(
            query_vector=query_embedding,
            limit=limit,
            filter=qdrant_filter
        )
        
        return results
        
    def generate_lesson_plan(self, query: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a lesson plan based on a query.
        
        Args:
            query: Query text
            filters: Optional filters to apply
            
        Returns:
            Generated lesson plan
        """
        # Search for relevant documents
        results = self.search(query, filters, limit=10)
        
        if not results:
            return {
                "error": "No relevant documents found",
                "query": query,
                "filters": filters
            }
            
        # Extract content from results
        contents = []
        metadata_list = []
        
        for result in results:
            # Extract payload
            payload = result.payload
            
            # Extract content
            if "text" in payload:
                contents.append(payload["text"])
                
            # Extract metadata
            if "metadata" in payload:
                metadata_list.append(payload["metadata"])
                
        # Get unique chapters
        chapters = set()
        for metadata in metadata_list:
            if "chapter" in metadata:
                chapters.add(metadata["chapter"])
                
        # Format the plan
        lesson_plan = {
            "title": f"Lesson Plan: {query}",
            "query": query,
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "sources": {
                "count": len(contents),
                "chapters": list(chapters)
            },
            "content": {
                "introduction": f"This lesson plan is designed to teach students about {query}.",
                "objectives": [
                    f"Understand the key concepts of {query}",
                    f"Apply knowledge of {query} to solve problems",
                    f"Analyze and evaluate information related to {query}"
                ],
                "main_content": contents[:3],  # First 3 content pieces
                "activities": [
                    f"Group discussion on {query}",
                    f"Problem-solving exercises related to {query}",
                    f"Research project on {query}"
                ],
                "assessment": f"Quiz on {query} concepts and applications",
                "conclusion": f"Review of key points about {query}"
            },
            "references": {
                "source_documents": [
                    {
                        "chapter": meta.get("chapter", "Unknown"),
                        "section": meta.get("section", "")
                    }
                    for meta in metadata_list[:5]  # First 5 metadata items
                ]
            }
        }
        
        return lesson_plan

def check_qdrant_collection():
    """
    Check if the Qdrant collection exists and has documents.
    
    Returns:
        True if collection exists and has documents, False otherwise
    """
    try:
        # Initialize connector
        db = QdrantConnector(
            host=QDRANT_HOST,
            port=QDRANT_PORT,
            collection_name=QDRANT_COLLECTION_NAME
        )
        
        # Get collection info
        collection_info = db.get_collection_info()
        
        # Check if collection exists and has vectors
        if collection_info and "vectors_count" in collection_info and collection_info["vectors_count"] > 0:
            logger.info(f"✅ Qdrant collection '{QDRANT_COLLECTION_NAME}' exists with {collection_info['vectors_count']} vectors")
            return True
        else:
            logger.warning(f"⚠️ Qdrant collection '{QDRANT_COLLECTION_NAME}' does not exist or has no vectors")
            return False
            
    except Exception as e:
        logger.error(f"Error checking Qdrant collection: {e}")
        return False

def setup_database():
    """
    Set up the database by running the data processing script.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Setting up database...")
        
        # Get the path to the process_improved_data.py script
        script_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "src", "scripts", "process_improved_data.py"
        )
        
        # Run the script
        os.system(f"python {script_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        return False

def save_lesson_plan(lesson_plan: Dict[str, Any], filename: str) -> bool:
    """
    Save a lesson plan to a file.
    
    Args:
        lesson_plan: Lesson plan to save
        filename: Name of the file to save to
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure the output directory exists
        os.makedirs(LESSON_PLANS_DIR, exist_ok=True)
        
        # Sanitize filename
        safe_filename = filename.replace(" ", "_").lower()
        if not safe_filename.endswith(".json"):
            safe_filename += ".json"
            
        # Create full path
        filepath = os.path.join(LESSON_PLANS_DIR, safe_filename)
        
        # Save the lesson plan
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(lesson_plan, f, indent=2)
            
        logger.info(f"✅ Saved lesson plan to {filepath}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving lesson plan: {e}")
        return False

def main():
    """Main function to run the pipeline."""
    logger.info("Starting EduPlan AI improved pipeline")
    
    # Check if the database is ready
    if not check_qdrant_collection():
        logger.info("Database not ready, setting up...")
        if not setup_database():
            logger.error("Failed to set up database")
            return
    
    # Initialize the lesson plan generator
    generator = LessonPlanGenerator()
    
    # Define example topics
    example_topics = [
        "Atomic theory and molecular structure",
        "Laws of motion and mechanical energy",
        "Cell biology and genetics",
        "Algebra and equation solving"
    ]
    
    # Generate and save lesson plans
    for topic in example_topics:
        logger.info(f"Generating lesson plan for topic: {topic}")
        
        # Generate the lesson plan
        lesson_plan = generator.generate_lesson_plan(topic)
        
        # Save the lesson plan
        filename = f"lesson_plan_{topic.replace(' ', '_').lower()}.json"
        save_lesson_plan(lesson_plan, filename)
    
    logger.info("Pipeline completed successfully")

if __name__ == "__main__":
    main()
