#!/usr/bin/env python3
"""Compare old vs improved PDF extraction quality"""

import json
import os

def compare_extractions():
    # Load improved extraction
    with open('data/processed_improved/Chapter_1_improved.json', 'r', encoding='utf-8') as f:
        new_data = json.load(f)
    
    # Load old extraction
    with open('data/processed/Chapter_1.pdf.json', 'r', encoding='utf-8') as f:
        old_data = json.load(f)
    
    print('COMPARISON: OLD vs NEW EXTRACTION')
    print('='*50)
    
    print('\nOLD EXTRACTION:')
    print('-' * 20)
    old_pages = old_data['Chapter_1.pdf']
    old_text = old_pages[0]['text'][:200] if old_pages else "No text"
    print(f'Pages: {len(old_pages)}')
    print(f'Sample text: {old_text}...')
    
    print('\nNEW IMPROVED EXTRACTION:')
    print('-' * 20)
    metadata = new_data['metadata']
    print(f'Chapter: {metadata["chapter_number"]} - {metadata["chapter_title"]}')
    print(f'Total words: {metadata["total_word_count"]}')
    print(f'Sections found: {len(new_data["sections"])}')
    print(f'Pages processed: {metadata["processed_pages"]}')
    
    # Show text quality comparison
    print('\nTEXT QUALITY COMPARISON:')
    print('-' * 30)
    
    # Old text sample
    print('OLD (first 200 chars):')
    print(repr(old_text[:200]))
    
    # New text sample  
    print('\nNEW (first 200 chars):')
    new_text = new_data['full_text'][:200]
    print(repr(new_text))
    
    # Show structured content
    if new_data['sections']:
        print('\nSTRUCTURED SECTIONS (first 3):')
        print('-' * 30)
        for i, section in enumerate(new_data['sections'][:3]):
            print(f'{i+1}. {section["title"][:50]}... ({section["type"]})')
            print(f'   Content items: {len(section["content"])}')
            print(f'   Activities: {len(section["activities"])}')
            print(f'   Questions: {len(section["questions"])}')

if __name__ == "__main__":
    compare_extractions()
