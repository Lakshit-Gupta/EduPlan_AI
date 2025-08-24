#!/usr/bin/env python3
"""
Improved PDF Text Extraction using PyMuPDF (fitz) and proper text processing
This script addresses issues with the current JSON extraction approach
"""

import fitz  # PyMuPDF
import re
import json
import os
from typing import List, Dict, Any
import sys

class ImprovedPDFExtractor:
    """Improved PDF text extraction with better structure and quality"""
    
    def __init__(self):
        self.output_dir = "data/processed_improved"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def extract_text_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Extract structured text from PDF using PyMuPDF"""
        try:
            doc = fitz.open(pdf_path)
            extracted_data = {
                'filename': os.path.basename(pdf_path),
                'total_pages': len(doc),
                'pages': []
            }
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Extract text with better formatting
                text = page.get_text("text")  # Plain text
                
                # Clean and process text
                cleaned_text = self.clean_text(text)
                
                # Extract text blocks for better structure
                blocks = page.get_text("dict")
                structured_text = self.extract_structured_text(blocks)
                
                page_data = {
                    'page_number': page_num + 1,
                    'raw_text': text,
                    'cleaned_text': cleaned_text,
                    'structured_text': structured_text,
                    'word_count': len(cleaned_text.split()) if cleaned_text else 0
                }
                
                # Only add pages with meaningful content
                if cleaned_text and len(cleaned_text.strip()) > 50:
                    extracted_data['pages'].append(page_data)
                else:
                    print(f"Warning: Page {page_num + 1} in {pdf_path} has insufficient text content")
            
            doc.close()
            return extracted_data
            
        except Exception as e:
            print(f"Error processing {pdf_path}: {e}")
            return None
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return ""
        
        # Remove excessive whitespace and newlines
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r' +', ' ', text)
        
        # Remove weird character repetitions (like MMMMM OOOOO SSSSS)
        text = re.sub(r'([A-Z])\1{3,}', r'\1', text)
        
        # Fix common OCR errors
        text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)  # Add space between lowercase and uppercase
        
        # Remove page headers/footers patterns
        text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)  # Remove standalone page numbers
        
        # Clean up chapter headers
        text = re.sub(r'^C\s*hapter\s*$', 'Chapter', text, flags=re.MULTILINE)
        
        return text.strip()
    
    def extract_structured_text(self, blocks_dict: Dict) -> List[Dict[str, Any]]:
        """Extract structured text from text blocks"""
        structured_content = []
        
        if 'blocks' not in blocks_dict:
            return structured_content
        
        for block in blocks_dict['blocks']:
            if 'lines' in block:
                block_text = ""
                font_info = []
                
                for line in block['lines']:
                    line_text = ""
                    for span in line['spans']:
                        line_text += span['text']
                        # Collect font information for structure analysis
                        font_info.append({
                            'font': span.get('font', ''),
                            'size': span.get('size', 0),
                            'flags': span.get('flags', 0)
                        })
                    block_text += line_text + " "
                
                if block_text.strip():
                    # Determine content type based on font info
                    content_type = self.classify_content_type(block_text, font_info)
                    
                    structured_content.append({
                        'text': block_text.strip(),
                        'type': content_type,
                        'bbox': block.get('bbox', [])
                    })
        
        return structured_content
    
    def classify_content_type(self, text: str, font_info: List[Dict]) -> str:
        """Classify content type based on text and font information"""
        text_lower = text.lower().strip()
        
        # Check for headings
        if any(font.get('size', 0) > 14 for font in font_info):
            if 'chapter' in text_lower:
                return 'chapter_title'
            return 'heading'
        
        # Check for specific content types
        if text_lower.startswith(('activity', 'experiment')):
            return 'activity'
        elif text_lower.startswith(('question', 'q.')):
            return 'question'
        elif 'figure' in text_lower or 'fig.' in text_lower:
            return 'figure_caption'
        elif 'table' in text_lower:
            return 'table_caption'
        else:
            return 'body_text'
    
    def extract_chapter_info(self, text: str) -> Dict[str, str]:
        """Extract chapter number and title from text"""
        chapter_info = {'number': '', 'title': ''}
        
        # Look for chapter patterns
        chapter_match = re.search(r'Chapter\s*(\d+)\s*[:\-]?\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
        if chapter_match:
            chapter_info['number'] = chapter_match.group(1)
            chapter_info['title'] = chapter_match.group(2).strip()
        
        return chapter_info
    
    def split_into_sections(self, pages: List[Dict]) -> List[Dict[str, Any]]:
        """Split content into logical sections with appropriate chunk sizes for embeddings"""
        sections = []
        current_section = None
        
        for page in pages:
            for content in page.get('structured_text', []):
                content_type = content['type']
                text = content['text']
                
                if content_type in ['chapter_title', 'heading']:
                    # Start new section
                    if current_section:
                        # Ensure content chunks are properly sized for embeddings
                        self._optimize_section_chunks(current_section)
                        sections.append(current_section)
                    
                    current_section = {
                        'title': text,
                        'type': content_type,
                        'content': [],
                        'activities': [],
                        'questions': []
                    }
                elif current_section:
                    # Add to current section
                    if content_type == 'activity':
                        current_section['activities'].append(text)
                    elif content_type == 'question':
                        current_section['questions'].append(text)
                    else:
                        current_section['content'].append(text)
        
        # Add last section
        if current_section:
            self._optimize_section_chunks(current_section)
            sections.append(current_section)
        
        return sections
    
    def _optimize_section_chunks(self, section: Dict[str, Any]) -> None:
        """Optimize section content chunks for better embeddings (around 500 tokens)"""
        # Target length for optimal embedding chunks (around 2000-2500 chars ~ 500 tokens)
        TARGET_CHUNK_LENGTH = 2000
        MIN_CHUNK_LENGTH = 200
        
        # Process regular content
        if 'content' in section and section['content']:
            new_content = []
            current_chunk = ""
            
            for text in section['content']:
                # If this would make the chunk too big, save current and start new
                if len(current_chunk) + len(text) > TARGET_CHUNK_LENGTH and len(current_chunk) > MIN_CHUNK_LENGTH:
                    new_content.append(current_chunk.strip())
                    current_chunk = text
                else:
                    # Add to current chunk
                    if current_chunk:
                        current_chunk += " " + text
                    else:
                        current_chunk = text
            
            # Don't forget the last chunk
            if current_chunk:
                new_content.append(current_chunk.strip())
                
            section['content'] = new_content
        
        # Also combine very short activities
        if 'activities' in section and section['activities']:
            new_activities = []
            current_chunk = ""
            
            for activity in section['activities']:
                if len(current_chunk) + len(activity) > TARGET_CHUNK_LENGTH and len(current_chunk) > MIN_CHUNK_LENGTH:
                    new_activities.append(current_chunk.strip())
                    current_chunk = activity
                else:
                    if current_chunk:
                        current_chunk += " " + activity
                    else:
                        current_chunk = activity
            
            if current_chunk:
                new_activities.append(current_chunk.strip())
            
            section['activities'] = new_activities
        
        # Same for questions
        if 'questions' in section and section['questions']:
            new_questions = []
            current_chunk = ""
            
            for question in section['questions']:
                if len(current_chunk) + len(question) > TARGET_CHUNK_LENGTH and len(current_chunk) > MIN_CHUNK_LENGTH:
                    new_questions.append(current_chunk.strip())
                    current_chunk = question
                else:
                    if current_chunk:
                        current_chunk += " " + question
                    else:
                        current_chunk = question
            
            if current_chunk:
                new_questions.append(current_chunk.strip())
            
            section['questions'] = new_questions
    
    def process_single_pdf(self, pdf_path: str) -> bool:
        """Process a single PDF file"""
        print(f"Processing {pdf_path}...")
        
        extracted_data = self.extract_text_from_pdf(pdf_path)
        if not extracted_data:
            return False
        
        # Extract chapter information
        all_text = " ".join([page['cleaned_text'] for page in extracted_data['pages']])
        chapter_info = self.extract_chapter_info(all_text)
        
        # Split into sections
        sections = self.split_into_sections(extracted_data['pages'])
        
        # Create final structure
        final_data = {
            'metadata': {
                'filename': extracted_data['filename'],
                'total_pages': extracted_data['total_pages'],
                'chapter_number': chapter_info['number'],
                'chapter_title': chapter_info['title'],
                'processed_pages': len(extracted_data['pages']),
                'total_word_count': sum(page['word_count'] for page in extracted_data['pages'])
            },
            'sections': sections,
            'full_text': all_text
        }
        
        # Save to JSON
        output_filename = f"{os.path.splitext(extracted_data['filename'])[0]}_improved.json"
        output_path = os.path.join(self.output_dir, output_filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved improved extraction to {output_path}")
        print(f"   - Pages processed: {len(extracted_data['pages'])}")
        print(f"   - Sections found: {len(sections)}")
        print(f"   - Total words: {final_data['metadata']['total_word_count']}")
        
        return True
    
    def process_all_pdfs(self, pdf_directory: str = "data/raw"):
        """Process all PDF files in the directory"""
        if not os.path.exists(pdf_directory):
            print(f"Error: Directory {pdf_directory} not found!")
            return
        
        pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith('.pdf')]
        
        if not pdf_files:
            print(f"No PDF files found in {pdf_directory}")
            return
        
        print(f"Found {len(pdf_files)} PDF files to process...")
        
        success_count = 0
        for pdf_file in sorted(pdf_files):
            pdf_path = os.path.join(pdf_directory, pdf_file)
            if self.process_single_pdf(pdf_path):
                success_count += 1
        
        print(f"\n🎉 Processing complete!")
        print(f"Successfully processed: {success_count}/{len(pdf_files)} files")

def main():
    """Main function"""
    extractor = ImprovedPDFExtractor()
    
    if len(sys.argv) > 1:
        # Process specific file
        pdf_path = sys.argv[1]
        extractor.process_single_pdf(pdf_path)
    else:
        # Process all files
        extractor.process_all_pdfs()

if __name__ == "__main__":
    main()
