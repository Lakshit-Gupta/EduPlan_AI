import sys
import os
import pytest

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import chunk_text, extract_metadata

def test_text_chunking():
    """Test text chunking functionality"""
    # Test case 1: Simple chunking
    text = "This is a test document. " * 100
    chunks = chunk_text(text, chunk_size=20, chunk_overlap=5)
    
    # Check if chunks were created
    assert len(chunks) > 1
    
    # Check if the first chunk has proper length
    words_in_first_chunk = len(chunks[0].split())
    assert words_in_first_chunk <= 20
    
    # Check if there's overlap
    if len(chunks) >= 2:
        last_words_first_chunk = chunks[0].split()[-5:]
        first_words_second_chunk = chunks[1].split()[:5]
        
        # At least some words should overlap
        assert any(word in first_words_second_chunk for word in last_words_first_chunk)

def test_metadata_extraction():
    """Test metadata extraction from filename"""
    # Create a test file path
    file_path = os.path.join("data", "sample_documents", "class7_math_algebra.txt")
    content = "This is a test document about algebra for intermediate students."
    
    # Extract metadata
    metadata = extract_metadata(file_path, content)
    
    # Check extracted values
    assert metadata["class"] == "7"
    assert metadata["subject"] == "math"
    assert metadata["topic"] == "algebra"
    assert metadata["difficulty"] == "intermediate"

if __name__ == "__main__":
    pytest.main(["-v", __file__])
