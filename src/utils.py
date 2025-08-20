import os
import re
from typing import List, Dict, Any, Tuple
import PyPDF2
import docx2txt
import config

def read_document(file_path: str) -> str:
    """
    Read document content from various file formats
    
    Args:
        file_path: Path to the document
        
    Returns:
        Document text content
    """
    file_extension = file_path.split('.')[-1].lower()
    
    if file_extension == 'pdf':
        return read_pdf(file_path)
    elif file_extension == 'docx':
        return read_docx(file_path)
    elif file_extension == 'txt':
        return read_text(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")

def read_pdf(file_path: str) -> str:
    """Extract text from PDF files"""
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    return text

def read_docx(file_path: str) -> str:
    """Extract text from DOCX files"""
    return docx2txt.process(file_path)

def read_text(file_path: str) -> str:
    """Read text files"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def extract_metadata(file_path: str, content: str) -> Dict[str, Any]:
    """
    Extract metadata from document filename and content
    
    Args:
        file_path: Path to the document
        content: Document content
        
    Returns:
        Dictionary with metadata fields
    """
    filename = os.path.basename(file_path)
    
    # Parse class from filename (assuming format like class5_math_fractions.txt)
    class_match = re.search(r'class(\d+)', filename.lower())
    class_number = class_match.group(1) if class_match else "unknown"
    
    # Parse subject from filename
    subject_match = re.search(r'class\d+_(\w+)', filename.lower())
    subject = subject_match.group(1) if subject_match else "unknown"
    
    # Parse chapter/topic from filename
    topic_match = re.search(r'class\d+_\w+_(.+)\.\w+$', filename.lower())
    topic = topic_match.group(1) if topic_match else "unknown"
    
    # Try to determine difficulty level from content (simple heuristic)
    if "advanced" in content.lower() or "challenging" in content.lower():
        difficulty = "advanced"
    elif "intermediate" in content.lower() or "moderate" in content.lower():
        difficulty = "intermediate"
    else:
        difficulty = "basic"
    
    return {
        "class": class_number,
        "subject": subject,
        "topic": topic,
        "difficulty": difficulty,
        "filename": filename,
        "created_at": os.path.getctime(file_path),
        "updated_at": os.path.getmtime(file_path)
    }

def chunk_text(text: str, chunk_size: int = None, chunk_overlap: int = None) -> List[str]:
    """
    Split text into overlapping chunks
    
    Args:
        text: Input text to be chunked
        chunk_size: Size of each chunk in tokens (approximated by words)
        chunk_overlap: Number of tokens to overlap between chunks
    
    Returns:
        List of text chunks
    """
    if chunk_size is None:
        chunk_size = config.CHUNK_SIZE
    if chunk_overlap is None:
        chunk_overlap = config.CHUNK_OVERLAP
    
    # Simple word-based chunking (approximation of tokens)
    words = text.split()
    
    chunks = []
    for i in range(0, len(words), chunk_size - chunk_overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        chunks.append(chunk)
        
        # Break if we've processed all words
        if i + chunk_size >= len(words):
            break
    
    return chunks

def process_document(file_path: str) -> Tuple[List[str], Dict[str, Any]]:
    """
    Process a document: read, extract metadata, and chunk
    
    Args:
        file_path: Path to the document
    
    Returns:
        Tuple of (chunks, metadata)
    """
    # Read document
    content = read_document(file_path)
    
    # Extract metadata
    metadata = extract_metadata(file_path, content)
    
    # Chunk document
    chunks = chunk_text(content)
    
    return chunks, metadata
