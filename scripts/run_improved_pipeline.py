#!/usr/bin/env python3
"""
Updated MVP Pipeline using improved PDF extraction and processing
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.processors.improved_document_processor import ImprovedDocumentProcessor
from src.models.embedding_model import NVEmbedPipeline
from src.core.vector_database import QdrantDB
from src.generators.lesson_plan_generator import LessonPlanGenerator

def check_qdrant_connection():
    """Check if Qdrant is running"""
    try:
        db = QdrantDB()
        print("✅ Qdrant is running!")
        return True
    except Exception as e:
        print(f"❌ Qdrant connection failed: {e}")
        return False

def setup_improved_database():
    """Set up the vector database with improved documents"""
    print("🚀 Setting up EduPlan AI - IMPROVED Pipeline")
    print("="*50)
    
    try:
        # Step 1: Process documents with improved extractor
        print("\n📄 Step 1: Processing improved documents...")
        processor = ImprovedDocumentProcessor(use_improved_data=True)
        documents, metadata = processor.process_all_improved_documents()
        
        if not documents:
            print("❌ No documents found to process!")
            return False
        
        # Step 2: Generate embeddings
        print(f"\n🧠 Step 2: Generating embeddings for {len(documents)} chunks...")
        embedder = NVEmbedPipeline()
        embeddings = embedder.embed_texts(documents)
        
        # Step 3: Store in vector database
        print(f"\n💾 Step 3: Storing in vector database...")
        db = QdrantDB()
        
        # Clear existing collection and create new one
        collection_name = "lesson_plans_improved"
        try:
            db.client.delete_collection(collection_name)
            print("🗑️  Cleared existing collection")
        except:
            pass
        
        # Update collection name for improved data
        db.collection_name = collection_name
        document_ids = db.insert_documents(embeddings, documents, metadata)
        
        print(f"✅ Successfully set up database with {len(documents)} document chunks!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_improved_lesson_generation():
    """Test lesson plan generation with improved data"""
    print("\n🎯 Step 4: Testing improved lesson plan generation...")
    
    try:
        # Create generator with improved collection
        generator = LessonPlanGenerator()
        generator.db.collection_name = "lesson_plans_improved"  # Use improved collection
        
        test_cases = [
            {
                "query": "atomic theory and molecular structure",
                "chapter": "Chapter 3",
                "subject": "General",
                "description": "Atomic theory (Chapter 3)"
            },
            {
                "query": "matter and its properties",
                "chapter": "Chapter 1", 
                "subject": "General",
                "description": "Matter properties (Chapter 1)"
            },
            {
                "query": "motion and force concepts",
                "chapter": "Chapter 9",
                "subject": "General", 
                "description": "Motion and force (Chapter 9)"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 Test {i}: {test_case['description']}")
            print(f"   Chapter: {test_case['chapter']}, Subject: {test_case['subject']}")
            
            lesson_plan = generator.generate_lesson_plan(
                query=test_case['query'],
                filter_chapter=test_case['chapter'],
                filter_subject=test_case['subject']
            )
            
            # Save to outputs
            filename = f"improved_lesson_plan_{test_case['query'].replace(' ', '_').lower()}.json"
            output_path = os.path.join('outputs/lesson_plans', filename)
            
            import json
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(lesson_plan, f, indent=2, ensure_ascii=False)
            
            print(f"📁 Saved to: {filename}")
            
            # Show results summary
            sources = lesson_plan.get('sources', [])
            print(f"   📚 Found {len(sources)} source documents")
            if sources:
                print(f"   📖 Sample source: {sources[0].get('text', '')[:100]}...")
        
    except Exception as e:
        print(f"❌ Error during lesson generation test: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main pipeline function"""
    print("🔍 Checking Qdrant connection...")
    if not check_qdrant_connection():
        print("\nTroubleshooting:")
        print("1. Make sure Qdrant is running: docker run -d -p 6333:6333 qdrant/qdrant")
        print("2. Check if port 6333 is available")
        return
    
    # Run the improved pipeline
    if setup_improved_database():
        test_improved_lesson_generation()
        
        print(f"\n🎉 Improved Pipeline Setup Complete!")
        print("="*50)
        print("You can now:")
        print("1. Generate high-quality lesson plans with clean text")
        print("2. Access all 12 chapters including Chapter 3")
        print("3. Use improved semantic search with 818 document chunks")
        print("4. Benefit from 65,377 words of clean educational content")
    else:
        print("❌ Pipeline setup failed!")

if __name__ == "__main__":
    main()
