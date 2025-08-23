#!/usr/bin/env python3
"""
EduPlan AI - Main Entry Point
Educational AI Platform for RAG-based lesson plan generation
"""

import sys
import os
import argparse

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main entry point for EduPlan AI"""
    parser = argparse.ArgumentParser(description='EduPlan AI - Educational AI Platform')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Set up the RAG pipeline')
    setup_parser.add_argument('--force', action='store_true', help='Force rebuild of database')
    
    # Generate command  
    generate_parser = subparsers.add_parser('generate', help='Generate lesson plan')
    generate_parser.add_argument('topic', help='Lesson plan topic')
    generate_parser.add_argument('--chapter', help='Filter by chapter (e.g., Chapter 3)')
    generate_parser.add_argument('--subject', default='General', help='Filter by subject')
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check database status')
    
    args = parser.parse_args()
    
    if args.command == 'setup':
        print("🚀 Running EduPlan AI Setup...")
        os.system('python scripts/run_mvp_pipeline.py')
        
    elif args.command == 'generate':
        print(f"📝 Generating lesson plan for: {args.topic}")
        from src.generators.lesson_plan_generator import LessonPlanGenerator
        
        generator = LessonPlanGenerator()
        lesson_plan = generator.generate_lesson_plan(
            query=args.topic,
            filter_chapter=args.chapter,
            filter_subject=args.subject
        )
        
        # Save lesson plan
        import json
        filename = f"lesson_plan_{args.topic.replace(' ', '_').lower()}.json"
        output_path = os.path.join('outputs/lesson_plans', filename)
        
        with open(output_path, 'w') as f:
            json.dump(lesson_plan, f, indent=2)
            
        print(f"✅ Lesson plan saved to: {output_path}")
        
    elif args.command == 'check':
        print("🔍 Checking database status...")
        os.system('python scripts/check_database.py')
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
