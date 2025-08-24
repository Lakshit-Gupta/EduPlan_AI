"""
Configuration settings for the EduPlan AI system.
This module contains configuration parameters for data paths, models, and databases.
"""

import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = os.path.join(BASE_DIR, 'data')
OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')

# Data directories
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')
PROCESSED_IMPROVED_DIR = os.path.join(DATA_DIR, 'processed_improved')

# Output directories
LESSON_PLANS_DIR = os.path.join(OUTPUTS_DIR, 'lesson_plans')

# Embedding model configuration
EMBEDDING_MODEL = "nvidia/NV-Embed-v2"  # Using NV-Embed
EMBEDDING_BATCH_SIZE = 2
EMBEDDING_MAX_LENGTH = 512

# Vector database configuration
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
QDRANT_COLLECTION_NAME = "science_9_collection"
QDRANT_VECTOR_SIZE = 4096  # NV-Embed dimensions

# Ensure directories exist
os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
os.makedirs(PROCESSED_IMPROVED_DIR, exist_ok=True)
os.makedirs(LESSON_PLANS_DIR, exist_ok=True)
