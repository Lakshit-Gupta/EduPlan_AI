#!/usr/bin/env python3
"""
Improved Document Processor for the new high-quality JSON format
"""

import json
import os
from typing import List, Dict, Any, Union
import tiktoken
import sys

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from src.core.config import CHUNK_SIZE, CHUNK_OVERLAP

class ImprovedDocumentProcessor:
    """Process improved JSON documents for embedding with better quality"""
    
    def __init__(self, use_improved_data: bool = True):
        self.use_improved_data = use_improved_data
        self.data_dir = "data/processed_improved" if use_improved_data else "data/processed"
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")  # For token counting
    
    def load_improved_documents(self) -> List[Dict[str, Any]]:
        """Load all improved JSON documents"""
        documents = []
        
        if not os.path.exists(self.data_dir):
            print(f"Directory {self.data_dir} not found!")
            return documents
        
        for filename in sorted(os.listdir(self.data_dir)):
            if filename.endswith('_improved.json'):
                filepath = os.path.join(self.data_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        documents.append({
                            'filename': filename,
                            'data': data
                        })
                        print(f"✅ Loaded {filename} - {data['metadata']['total_word_count']} words")
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
        
        return documents
    
    def extract_text_from_improved_json(self, json_data: Dict) -> str:
        """Extract clean text from improved JSON structure"""
        # Use the full_text which is already cleaned
        full_text = json_data.get('full_text', '')
        
        if not full_text:
            # Fallback: extract from sections
            sections_text = []
            for section in json_data.get('sections', []):
                # Add section title
                if section.get('title'):
                    sections_text.append(section['title'])
                
                # Add content
                for content in section.get('content', []):
                    sections_text.append(content)
                
                # Add activities
                for activity in section.get('activities', []):
                    sections_text.append(f"Activity: {activity}")
                
                # Add questions
                for question in section.get('questions', []):
                    sections_text.append(f"Question: {question}")
            
            full_text = '\n\n'.join(sections_text)
        
        return full_text
    
    def extract_metadata_from_improved_json(self, filename: str, json_data: Dict) -> Dict[str, Any]:
        """Extract metadata from improved JSON structure"""
        metadata = json_data.get('metadata', {})
        
        # Extract chapter number from metadata or filename
        chapter_number = metadata.get('chapter_number', '')
        if not chapter_number:
            # Extract from filename
            import re
            match = re.search(r'Chapter_(\d+)', filename)
            chapter_number = match.group(1) if match else 'Unknown'
        
        # Map to our expected format
        processed_metadata = {
            'chapter': f'Chapter {chapter_number}' if chapter_number else 'Chapter Unknown',
            'subject': 'General',  # Can be enhanced later
            'difficulty': 'Basic',  # Can be enhanced based on content analysis
            'source_file': filename,
            'word_count': metadata.get('total_word_count', 0),
            'pages': metadata.get('processed_pages', 0),
            'sections': len(json_data.get('sections', [])),
            'chapter_title': metadata.get('chapter_title', '')
        }
        
        return processed_metadata
    
    def chunk_text_improved(self, text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
        """Split text into chunks with improved boundary detection"""
        if not text.strip():
            return []
        
        # Tokenize text
        tokens = self.encoding.encode(text)
        
        if len(tokens) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(tokens):
            end = start + chunk_size
            
            # Extract chunk tokens
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoding.decode(chunk_tokens)
            
            # Try to end at sentence boundary
            if end < len(tokens):
                # Look for sentence endings in the last part
                sentences = chunk_text.split('.')
                if len(sentences) > 1:
                    # Keep all but the last incomplete sentence
                    chunk_text = '.'.join(sentences[:-1]) + '.'
                    # Recalculate tokens for the adjusted chunk
                    chunk_tokens = self.encoding.encode(chunk_text)
            
            chunks.append(chunk_text.strip())
            
            # Move start position with overlap
            start = max(start + len(chunk_tokens) - overlap, start + 1)
        
        return [chunk for chunk in chunks if chunk.strip()]
    
    def process_all_improved_documents(self) -> tuple[List[str], List[Dict[str, Any]]]:
        """Process all improved documents and return chunks with metadata"""
        documents = self.load_improved_documents()
        
        all_chunks = []
        all_metadata = []
        
        print(f"\n📄 Processing {len(documents)} improved documents...")
        
        for doc in documents:
            filename = doc['filename']
            json_data = doc['data']
            
            # Extract text
            text = self.extract_text_from_improved_json(json_data)
            
            if not text.strip():
                print(f"⚠️  Skipping {filename} - no text content")
                continue
            
            # Extract metadata
            base_metadata = self.extract_metadata_from_improved_json(filename, json_data)
            
            # Chunk text
            chunks = self.chunk_text_improved(text)
            
            print(f"📝 {filename}: {len(chunks)} chunks from {base_metadata['word_count']} words")
            
            # Add chunks with metadata
            for i, chunk in enumerate(chunks):
                chunk_metadata = base_metadata.copy()
                chunk_metadata['chunk_index'] = i
                chunk_metadata['chunk_text_preview'] = chunk[:100] + "..." if len(chunk) > 100 else chunk
                
                all_chunks.append(chunk)
                all_metadata.append(chunk_metadata)
        
        print(f"✅ Total chunks processed: {len(all_chunks)}")
        return all_chunks, all_metadata
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics of the improved data"""
        documents = self.load_improved_documents()
        
        stats = {
            'total_documents': len(documents),
            'chapters': {},
            'total_words': 0,
            'total_sections': 0,
            'total_pages': 0
        }
        
        for doc in documents:
            data = doc['data']
            metadata = data.get('metadata', {})
            
            chapter_num = metadata.get('chapter_number', 'Unknown')
            chapter_title = metadata.get('chapter_title', 'Unknown')
            
            stats['chapters'][f'Chapter {chapter_num}'] = {
                'title': chapter_title,
                'words': metadata.get('total_word_count', 0),
                'sections': len(data.get('sections', [])),
                'pages': metadata.get('processed_pages', 0)
            }
            
            stats['total_words'] += metadata.get('total_word_count', 0)
            stats['total_sections'] += len(data.get('sections', []))
            stats['total_pages'] += metadata.get('processed_pages', 0)
        
        return stats

def main():
    """Test the improved document processor"""
    processor = ImprovedDocumentProcessor(use_improved_data=True)
    
    print("📊 IMPROVED DATA STATISTICS")
    print("=" * 40)
    stats = processor.get_summary_stats()
    print(f"Total documents: {stats['total_documents']}")
    print(f"Total words: {stats['total_words']:,}")
    print(f"Total sections: {stats['total_sections']}")
    print(f"Total pages: {stats['total_pages']}")
    
    print("\nChapter breakdown:")
    for chapter, info in stats['chapters'].items():
        print(f"  {chapter}: {info['words']:,} words, {info['sections']} sections")
    
    print("\n📄 PROCESSING TEST")
    print("=" * 40)
    chunks, metadata = processor.process_all_improved_documents()
    
    print(f"\nSample chunk from Chapter 1:")
    if chunks:
        sample_chunk = chunks[0]
        sample_meta = metadata[0]
        print(f"Chapter: {sample_meta['chapter']}")
        print(f"Words: {len(sample_chunk.split())}")
        print(f"Preview: {sample_chunk[:200]}...")

if __name__ == "__main__":
    main()
