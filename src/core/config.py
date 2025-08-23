# Configuration for EduPlan AI Platform - Day 1 RAG System

# Qdrant Configuration  
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
QDRANT_COLLECTION_NAME = "lesson_plans"
QDRANT_VECTOR_SIZE = 1024  # nv-embed dimension (fallback: 384 for sentence-transformers)

# Embedding Configuration
EMBEDDING_MODEL = "nvidia/nv-embed-text-latest"  # Primary choice
FALLBACK_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # Fallback

# Text Processing
CHUNK_SIZE = 512  # tokens
CHUNK_OVERLAP = 50  # tokens
BATCH_SIZE = 32

# Document Structure - Chapter-wise categorization (Chapter 1-12)
CHAPTER_CATEGORIES = [f"Chapter {i}" for i in range(1, 13)]

# Subjects for metadata tagging
SUBJECTS = [
    "Mathematics", "Science", "English", "Hindi", "Social Studies",
    "Physics", "Chemistry", "Biology", "History", "Geography"
]

# Difficulty levels for metadata
DIFFICULTY_LEVELS = ["Basic", "Intermediate", "Advanced"]

# Data paths
RAG_DATA_DIR = "data/raw"
EXTRACTED_DATA_DIR = "data/processed"
IMPROVED_DATA_DIR = "data/processed_improved"
OUTPUT_DIR = "outputs/lesson_plans"

# Retrieval settings
TOP_K_RESULTS = 5
SIMILARITY_THRESHOLD = 0.7