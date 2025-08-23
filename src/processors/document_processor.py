import json
import os
from typing import List, Dict, Any, Union
from ..core.config import EXTRACTED_DATA_DIR, CHUNK_SIZE, CHUNK_OVERLAP
import tiktoken

class DocumentProcessor:
    """Process extracted JSON documents for embedding"""
    
    def __init__(self):
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    def load_extracted_documents(self) -> List[Dict[str, Any]]:
        """Load all extracted JSON documents"""
        documents = []
        
        if not os.path.exists(EXTRACTED_DATA_DIR):
            print(f"Directory {EXTRACTED_DATA_DIR} not found!")
            return documents
        
        for filename in os.listdir(EXTRACTED_DATA_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(EXTRACTED_DATA_DIR, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        documents.append({
                            'filename': filename,
                            'content': data
                        })
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
        
        return documents
    
    def extract_text_from_json(self, json_data) -> str:
        """Extract all text content from JSON structure"""
        text_content = []
        
        # Handle different JSON structures
        if isinstance(json_data, list):
            # Handle list format (malformed files)
            for item in json_data:
                if isinstance(item, dict):
                    # Process as if it's a single PDF entry
                    for key, pages in item.items():
                        if isinstance(pages, list):
                            for page in pages:
                                self._extract_page_text(page, text_content)
        elif isinstance(json_data, dict):
            # Handle standard dict format
            for pdf_name, pages in json_data.items():
                if isinstance(pages, list):
                    for page in pages:
                        self._extract_page_text(page, text_content)
        
        # Filter out None and empty strings
        text_content = [text for text in text_content if text and text.strip()]
        return '\n\n'.join(text_content)
    
    def _extract_page_text(self, page: dict, text_content: list):
        """Extract text from a single page"""
        # Add extracted text
        if page.get('text') and page['text'].strip():
            text_content.append(page['text'])
        
        # Add OCR text if available
        if page.get('ocr') and page['ocr'].strip():
            text_content.append(page['ocr'])
        
        # Add table content
        if page.get('tables'):
            for table in page['tables']:
                if table:
                    # Handle nested lists and None values in tables
                    table_text_parts = []
                    for row in table:
                        if row:
                            row_text = ' '.join([cell if cell is not None else '' for cell in row])
                            if row_text.strip():
                                table_text_parts.append(row_text)
                    if table_text_parts:
                        text_content.append(' '.join(table_text_parts))
        return ' '.join(text_content)
    
    def chunk_text(self, text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
        """Split text into overlapping chunks"""
        tokens = self.tokenizer.encode(text)
        chunks = []
        
        for i in range(0, len(tokens), chunk_size - overlap):
            chunk_tokens = tokens[i:i + chunk_size]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            chunks.append(chunk_text)
        
        return chunks
    
    def extract_metadata(self, filename: str, chunk_idx: int) -> Dict[str, Any]:
        """Extract metadata from filename and content - Chapter-wise categorization"""
        metadata = {
            'source_file': filename,
            'chunk_index': chunk_idx,
            'chapter': 'Chapter 1',  # Default
            'subject': 'General',  # Default  
            'difficulty': 'Basic'   # Default
        }
        
        # Extract chapter from filename (Chapter 1-12)
        for i in range(1, 13):
            if f'chapter{i}' in filename.lower() or f'chapter_{i}' in filename.lower() or f'chapter {i}' in filename.lower():
                metadata['chapter'] = f'Chapter {i}'
                break
        
        # Try to extract subject from filename
        subjects = ['math', 'science', 'english', 'hindi', 'social', 'physics', 'chemistry', 'biology', 'history', 'geography']
        for subject in subjects:
            if subject in filename.lower():
                metadata['subject'] = subject.capitalize()
                break
        
        # Determine difficulty from content length and complexity (simple heuristic)
        if chunk_idx == 0:  # First chunk often contains basic introduction
            metadata['difficulty'] = 'Basic'
        elif chunk_idx < 3:
            metadata['difficulty'] = 'Intermediate'  
        else:
            metadata['difficulty'] = 'Advanced'
        
        return metadata
    
    def process_all_documents(self) -> List[Dict[str, Any]]:
        """Process all documents and return chunks with metadata"""
        documents = self.load_extracted_documents()
        processed_chunks = []
        
        for doc in documents:
            # Extract text from JSON
            text = self.extract_text_from_json(doc['content'])
            
            if not text.strip():
                continue
            
            # Split into chunks
            chunks = self.chunk_text(text)
            
            # Create chunk documents with metadata
            for i, chunk in enumerate(chunks):
                if len(chunk.strip()) > 50:  # Only include substantial chunks
                    processed_chunks.append({
                        'text': chunk,
                        'metadata': self.extract_metadata(doc['filename'], i)
                    })
        
        print(f"Processed {len(processed_chunks)} chunks from {len(documents)} documents")
        return processed_chunks

if __name__ == "__main__":
    processor = DocumentProcessor()
    chunks = processor.process_all_documents()
    print(f"Total chunks: {len(chunks)}")
    if chunks:
        print("Sample chunk:", chunks[0])