# Configuration for EduPlan AI Platform

# Database Settings
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
QDRANT_COLLECTION_NAME = "lesson_plans"
QDRANT_VECTOR_SIZE = 384  # all-MiniLM-L6-v2 dimension

# Embedding Settings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Using SentenceTransformers model
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
BATCH_SIZE = 16

# Retrieval Settings
TOP_K_RESULTS = 5
SIMILARITY_THRESHOLD = 0.7

# Generation Settings
TEMPERATURE = 0.2
MAX_TOKENS = 1500
MODEL_NAME = "gpt2"  # Simple model for MVP

# API Settings (Flask)
API_HOST = "127.0.0.1"
API_PORT = 5000
DEBUG = True

# Document Processing
ALLOWED_EXTENSIONS = ["pdf", "txt", "docx"]

# Class Categories (1-12)
CLASS_CATEGORIES = [str(i) for i in range(1, 13)]
