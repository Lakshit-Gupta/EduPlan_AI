#!/usr/bin/env python3
"""
Analyze current JSON structure to understand the data format
"""
import json
import os

def analyze_json_files():
    files_to_check = ['Chapter_1.pdf.json', 'Chapter_2.pdf.json', 'Chapter_5.pdf.json']
    
    for filename in files_to_check:
        path = f'data/processed/{filename}'
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f'\n{filename}:')
            print(f'  Type: {type(data)}')
            
            if isinstance(data, dict):
                for key, value in data.items():
                    print(f'  Key: {key}')
                    print(f'  Value Type: {type(value)}')
                    if isinstance(value, list):
                        print(f'  Length: {len(value)}')
                        if len(value) > 0:
                            first_item = value[0]
                            print(f'    First item type: {type(first_item)}')
                            if isinstance(first_item, dict):
                                print(f'    First item keys: {list(first_item.keys())}')
                                # Check text content
                                text_content = first_item.get('text', '')
                                ocr_content = first_item.get('ocr', '')
                                print(f'    Text length: {len(text_content)}')
                                print(f'    OCR length: {len(ocr_content)}')
                                print(f'    Text preview: {text_content[:100]}...' if text_content else '    No text content')

if __name__ == "__main__":
    analyze_json_files()
