#!/usr/bin/env python3
"""
EduPlan AI - MVP Pipeline: Lesson Plan Generation System
This script sets up the complete RAG pipeline for generating lesson plans
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.processors.document_processor import DocumentProcessor
from src.models.embedding_model import NVEmbedPipeline
from src.core.vector_database import QdrantDB
from src.generators.lesson_plan_generator import LessonPlanGenerator

def setup_database():
    """Set up the vector database with documents"""
    print("🚀 Setting up EduPlan AI - MVP Pipeline")
    print("=" * 50)
    
    # Step 1: Process documents
    print("\n📄 Step 1: Processing documents...")
    processor = DocumentProcessor()
    chunks = processor.process_all_documents()
    
    if not chunks:
        print("❌ No documents found! Please:")
        print("1. Place PDF files in 'rag_data' folder")
        print("2. Run: python pdf_ocr_to_json.py")
        return False
    
    # Step 2: Generate embeddings
    print("\n🧠 Step 2: Generating embeddings...")
    embedder = NVEmbedPipeline()
    texts = [chunk['text'] for chunk in chunks]
    embeddings = embedder.embed_texts(texts)
    
    # Step 3: Store in Qdrant
    print("\n💾 Step 3: Storing in vector database...")
    db = QdrantDB()
    metadata = [chunk['metadata'] for chunk in chunks]
    doc_ids = db.insert_documents(embeddings, texts, metadata)
    
    print(f"✅ Successfully set up database with {len(doc_ids)} document chunks!")
    return True

def test_lesson_plan_generation():
    """Test the lesson plan generation"""
    print("\n🎯 Step 4: Testing lesson plan generation...")
    
    generator = LessonPlanGenerator()
    
    # Test queries with Chapter-wise filtering
    test_queries = [
        ("Atomic theory and molecular structure", "Chapter 3", "Science"),
        ("Introduction to basic mathematical concepts", "Chapter 1", "Mathematics"), 
        ("Chemical reactions and conservation laws", "Chapter 3", "Science")
    ]
    
    for i, (query, chapter, subject) in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        print(f"   Chapter: {chapter}, Subject: {subject}")
        result = generator.generate_lesson_plan(query, chapter, subject)
        print(f"✅ Generated lesson plan with {len(result['sources'])} source documents")
        
        # Save lesson plan
        filename = f"lesson_plan_{chapter.lower().replace(' ', '_')}_{subject.lower()}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(result['lesson_plan'])
        print(f"📁 Saved to: {filename}")

def main():
    """Main function to run the complete setup"""
    try:
        # Check if Qdrant is running
        print("🔍 Checking Qdrant connection...")
        db = QdrantDB()
        print("✅ Qdrant is running!")
        
        # Set up the system
        if setup_database():
            test_lesson_plan_generation()
            
            print("\n🎉 Day 1 MVP Setup Complete!")
            print("=" * 50)
            print("You can now:")
            print("1. Generate lesson plans using lesson_plan_generator.py")
            print("2. Test the Flask API (if implemented)")
            print("3. Add more documents and re-run this script")
            
        else:
            print("\n❌ Setup failed. Please check your documents and try again.")
            
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure Qdrant is running: docker ps")
        print("2. Check if documents are processed: ls extracted_data/")
        print("3. Verify requirements: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
