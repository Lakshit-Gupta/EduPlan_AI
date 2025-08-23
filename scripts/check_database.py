#!/usr/bin/env python3
"""Check Qdrant data to verify metadata assignment"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.vector_database import QdrantDB

def check_qdrant_data():
    connector = QdrantDB()
    print('📊 Checking Qdrant collection info...')
    
    info = connector.client.get_collection('lesson_plans')
    print(f'Total points: {info.points_count}')
    print(f'Vector size: {info.config.params.vectors.size}')

    # Get sample points to check metadata
    scroll_result = connector.client.scroll(
        collection_name='lesson_plans',
        limit=5,
        with_payload=True
    )
    
    print('\n🔍 Sample documents in database:')
    for i, point in enumerate(scroll_result[0]):
        print(f'\nDocument {i+1}:')
        print(f'  Chapter: {point.payload.get("chapter", "N/A")}')
        print(f'  Subject: {point.payload.get("subject", "N/A")}')
        print(f'  Difficulty: {point.payload.get("difficulty", "N/A")}')
        print(f'  Source File: {point.payload.get("source_file", "N/A")}')
        print(f'  Text Preview: {point.payload.get("text", "N/A")[:100]}...')
    
    # Check unique chapters and subjects
    print('\n📈 Getting unique chapters and subjects...')
    all_points = connector.client.scroll(
        collection_name='lesson_plans',
        limit=1000,
        with_payload=True
    )
    
    chapters = set()
    subjects = set()
    for point in all_points[0]:
        chapters.add(point.payload.get("chapter", "unknown"))
        subjects.add(point.payload.get("subject", "unknown"))
    
    print(f'Unique chapters: {sorted(chapters)}')
    print(f'Unique subjects: {sorted(subjects)}')

if __name__ == "__main__":
    check_qdrant_data()
