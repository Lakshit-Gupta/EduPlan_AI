# EduPlan AI - Lesson Plan Generation System

## Project Overview

EduPlan AI is an intelligent educational platform that leverages Retrieval-Augmented Generation (RAG) to automate lesson plan creation for classes 1–12. The system organizes curriculum documents, embeds them using NVIDIA nv-embed, and stores them in Qdrant for efficient semantic search. Teachers and students can query the system to generate curriculum-aligned lesson plans with structured objectives, activities, and assessments.

## Features

- **Document Management**: Class-wise document categorization with metadata tagging
- **Embedding Pipeline**: Text chunking with NVIDIA nv-embed integration
- **Retrieval System**: Semantic search with filters for class, subject, etc.
- **Generation Module**: Contextual lesson plan creation with structured output

## Technical Architecture

```
Document Ingestion → Text Processing → nv-embed Encoding → Qdrant Storage
                                                              ↓
User Query → Query Processing → Semantic Search → Context Retrieval → LLM Generation
```

## Project Structure

```
EduPlan_AI/
├── data/
│   └── sample_documents/       # Sample educational documents
├── src/
│   ├── api/                   # API endpoints
│   ├── database/              # Database connectors
│   ├── embedding/             # Embedding models
│   ├── generation/            # LLM generation
│   ├── retrieval/             # Document retrieval
│   ├── config.py              # Configuration
│   ├── ingestion_pipeline.py  # Document processing pipeline
│   ├── main.py                # CLI entry point
│   └── utils.py               # Utility functions
└── requirements.txt           # Dependencies
```

## Prerequisites

- Python 3.9+
- [Qdrant](https://qdrant.tech/) (vector database)
- NVIDIA GPU (optional, for better performance)

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/EduPlan_AI.git
cd EduPlan_AI
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Install and start Qdrant (using Docker):
```
docker pull qdrant/qdrant
docker run -p 6333:6333 -p 6334:6334 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant
```

## Usage

### Ingest Documents

```
python src/main.py ingest data/sample_documents
```

### Generate a Lesson Plan

```
python src/main.py generate "Create a lesson plan for teaching fractions to elementary students" --class-filter 5 --subject-filter math
```

### Start the API Server

```
python src/main.py api
```

Then access the API documentation at: http://localhost:8000/docs

## API Endpoints

- `POST /upload-document`: Upload and process educational documents
- `POST /generate-lesson-plan`: Generate a lesson plan based on query and filters
- `GET /classes`: Get list of available class categories
- `GET /health`: API health check

## Development

### Running Tests

```
pytest tests/
```

### Environment Variables

Create a `.env` file in the project root to override any settings in `config.py`.

## License

This project is licensed under the terms of the MIT license.
