import os
import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config
from ingestion_pipeline import DocumentIngestionPipeline
from generation.generator import LessonPlanGenerator
from api.api import main as run_api

def ingest_documents(args):
    """Process and ingest documents"""
    pipeline = DocumentIngestionPipeline()
    
    if os.path.isfile(args.path):
        # Process single file
        doc_ids, metadata = pipeline.ingest_file(args.path)
        print(f"Processed file: {args.path}")
        print(f"Generated {len(doc_ids)} chunks")
        print(f"Metadata: {metadata}")
    
    elif os.path.isdir(args.path):
        # Process directory
        results = pipeline.ingest_directory(args.path)
        
        print(f"Processed {len(results)} files:")
        for result in results:
            status = result["status"]
            if status == "success":
                print(f"✓ {result['file']} - {result['chunks']} chunks - Class {result['class']}")
            else:
                print(f"✗ {result['file']} - Error: {result.get('error')}")
    
    else:
        print(f"Path not found: {args.path}")
        return 1
    
    return 0

def generate_lesson_plan(args):
    """Generate a lesson plan"""
    generator = LessonPlanGenerator()
    
    # Generate plan
    result = generator.generate_lesson_plan(
        query=args.query,
        class_filter=args.class_filter,
        subject_filter=args.subject_filter,
        num_context_docs=args.num_docs
    )
    
    # Print lesson plan
    print("\n" + "=" * 50)
    print("GENERATED LESSON PLAN")
    print("=" * 50)
    print(result["lesson_plan"])
    print("\n" + "=" * 50)
    
    # Print metadata
    print("METADATA:")
    print(f"- Query: {result['metadata']['query']}")
    print(f"- Class: {result['metadata']['class']}")
    print(f"- Subject: {result['metadata']['subject']}")
    print(f"- Sources: {result['metadata']['num_sources']} documents")
    
    return 0

def start_api(args):
    """Start the FastAPI server"""
    run_api()
    return 0

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="EduPlan AI - Lesson Plan Generator")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Ingest command
    ingest_parser = subparsers.add_parser("ingest", help="Process and ingest documents")
    ingest_parser.add_argument("path", help="Path to file or directory to ingest")
    
    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate a lesson plan")
    generate_parser.add_argument("query", help="Query for lesson plan generation")
    generate_parser.add_argument("--class-filter", help="Filter by class (1-12)")
    generate_parser.add_argument("--subject-filter", help="Filter by subject")
    generate_parser.add_argument("--num-docs", type=int, default=5, help="Number of context documents")
    
    # API command
    api_parser = subparsers.add_parser("api", help="Start the API server")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute command
    if args.command == "ingest":
        return ingest_documents(args)
    elif args.command == "generate":
        return generate_lesson_plan(args)
    elif args.command == "api":
        return start_api(args)
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())
