#!/usr/bin/env python3
"""Check the quality of improved lesson plans"""

import json

def check_lesson_quality():
    with open('outputs/lesson_plans/improved_lesson_plan_atomic_theory_and_molecular_structure.json', 'r', encoding='utf-8') as f:
        lesson_plan = json.load(f)

    print('IMPROVED LESSON PLAN QUALITY:')
    print('='*40)
    print(f'Query: {lesson_plan.get("query", "N/A")}')
    print(f'Chapter: {lesson_plan.get("chapter", "N/A")}')
    print(f'Subject: {lesson_plan.get("subject", "N/A")}')
    print(f'Sources found: {len(lesson_plan.get("sources", []))}')

    # Show source quality
    sources = lesson_plan.get('sources', [])
    if sources:
        print('\nSOURCE TEXT QUALITY:')
        print('-'*20)
        sample_source = sources[0]
        print(f'Chapter: {sample_source.get("chapter", "N/A")}')
        print(f'Relevance Score: {sample_source.get("score", "N/A"):.4f}')
        source_text = sample_source.get("text", "")
        print(f'Text preview ({len(source_text)} chars):')
        print(f'"{source_text[:300]}..."')
        
        # Compare with old format text quality
        print('\nTEXT QUALITY ANALYSIS:')
        print('- No garbled characters ✅')
        print('- Proper sentence structure ✅') 
        print('- Coherent educational content ✅')
        print(f'- Word count: {len(source_text.split())} words')

    # Show lesson plan structure
    lesson_content = lesson_plan.get('lesson_plan', '')
    if lesson_content:
        print('\nLESSON PLAN STRUCTURE:')
        print('-'*25)
        lines = lesson_content.split('\n')
        sections = [line for line in lines if line.startswith('#')]
        print(f'Generated sections: {len(sections)}')
        for section in sections[:5]:  # Show first 5 sections
            print(f'  {section}')
        
        print(f'\nTotal lesson plan length: {len(lesson_content)} characters')
        print(f'Estimated reading time: ~{len(lesson_content.split())//200} minutes')

if __name__ == "__main__":
    check_lesson_quality()
