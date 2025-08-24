# EduPlan_AI

EduPlan_AI is a Retrieval-Augmented Generation (RAG) system designed to process educational content, generate embeddings, store them in a vector database, and use them to create customized lesson plans.

## System Overview

EduPlan_AI works through the following steps:

1. **Content Processing**: Educational content from textbooks is processed and converted to structured JSON format.
2. **Embedding Generation**: NVIDIA NV-Embed-v2 is used to generate high-quality semantic embeddings of the content.
3. **Vector Storage**: Embeddings are stored in a Qdrant vector database for efficient retrieval.
4. **Lesson Plan Generation**: When a topic is provided, relevant content is retrieved using semantic search and used to generate a lesson plan.

## Installation

### Prerequisites

- Python 3.8+
- Docker (for running Qdrant)
- CUDA-compatible GPU (for optimal performance)

### Setup

1. Clone the repository:
```
git clone https://github.com/lakshit-gupta/EduPlan_AI.git
cd EduPlan_AI
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Start the Qdrant server:
```
docker run -d -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

## Usage

1. Process data and generate embeddings:
```
python src/scripts/process_improved_data.py
```

2. Generate lesson plans:
```
python scripts/run_improved_pipeline.py
```

Generated lesson plans will be saved in `outputs/lesson_plans/`.

## Directory Structure

```
EduPlan_AI/
├── data/
│   ├── raw/                  # Raw educational content
│   ├── processed/            # Processed content
│   └── processed_improved/   # Improved processed content in JSON format
├── src/
│   ├── core/                 # Core configuration and utilities
│   ├── database/             # Database connectors
│   ├── models/               # Embedding models
│   └── scripts/              # Processing scripts
├── scripts/                  # Pipeline scripts
├── outputs/
│   └── lesson_plans/         # Generated lesson plans
└── README.md
```

## Configuration

You can customize the system by editing `src/core/config.py`, which contains parameters for:

- Data directories
- Model selection
- Vector database settings

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- NVIDIA for the NV-Embed model
- Qdrant for the vector database
