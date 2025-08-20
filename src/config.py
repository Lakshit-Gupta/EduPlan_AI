# Configuration for EduPlan AI Platform

# Database Settings
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
QDRANT_COLLECTION_NAME = "lesson_plans"
QDRANT_VECTOR_SIZE = 1024  # nv-embed default dimension

# Embedding Settings
EMBEDDING_MODEL = "nvidia/nv-embed-text-latest"
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
BATCH_SIZE = 16

# Retrieval Settings
TOP_K_RESULTS = 5
SIMILARITY_THRESHOLD = 0.7

# Generation Settings
TEMPERATURE = 0.2
MAX_TOKENS = 1500
MODEL_NAME = "nvidia/nv-embed-llm-next-latest"  # or your preferred LLM

# API Settings
API_HOST = "0.0.0.0"
API_PORT = 8000
DEBUG = True

# Document Processing
ALLOWED_EXTENSIONS = ["pdf", "txt", "docx"]

# Class Categories (1-12)
CLASS_CATEGORIES = [str(i) for i in range(1, 13)]
