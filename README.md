# 🎓 EduPlan AI - Educational AI Platform

An advanced **RAG-based educational AI platform** that generates personalized lesson plans by processing PDF textbooks and creating targeted content based on user queries. The system uses high-quality PDF extraction, vector embeddings, and retrieval-augmented generation to deliver contextual educational content.

## 🌟 Key Features

- **🔍 High-Quality PDF Extraction**: PyMuPDF-based extraction with text cleaning (818 quality chunks vs 381 poor chunks)
- **🧠 RAG Technology**: Retrieval-Augmented Generation for contextual lesson plans
- **📚 Chapter-Wise Organization**: Supports filtering by chapters and subjects
- **🎯 Targeted Generation**: Custom lesson plans based on specific topics
- **💾 Vector Database**: Qdrant integration for efficient similarity search
- **🖥️ CLI Interface**: Clean command-line interface with argparse

## 📊 Quality Improvements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Text Chunks | 381 | 818 | +115% |
| Text Quality | Poor (garbled) | High (clean) | Dramatic |
| Word Count | ~32K | 65,377 | +104% |
| Chapters Processed | 11 | 12 | Complete coverage |
| Project Organization | Scattered | Modular | Professional |

## 🏗️ Project Structure

```
EduPlan_AI/
├── 📄 main.py                           # Central CLI entry point
├── 📄 README.md                         # This comprehensive guide
├── 📄 requirements.txt                  # Python dependencies
│
├── 📁 src/                              # Core application modules
│   ├── 📁 core/                         # Core functionality
│   │   ├── config.py                    # Configuration management
│   │   └── vector_database.py           # Qdrant database operations
│   ├── 📁 models/                       # Data models & AI models
│   │   └── embedding_model.py           # NVIDIA nv-embed + fallbacks
│   ├── 📁 processors/                   # Document processing
│   │   ├── document_processor.py        # Legacy processor
│   │   └── improved_document_processor.py  # High-quality processor
│   └── 📁 generators/                   # Content generation
│       └── lesson_plan_generator.py     # Main lesson plan generator
│
├── 📁 scripts/                          # Utility scripts
│   ├── improved_pdf_extractor.py        # High-quality PDF extraction
│   ├── run_improved_pipeline.py         # New processing pipeline
│   ├── check_database.py               # Database verification
│   ├── analyze_json.py                 # Data analysis tools
│   └── show_project_structure.py       # Project visualization
│
├── 📁 data/                             # Data files
│   ├── 📁 raw/                          # Original PDF textbooks (12 chapters)
│   ├── 📁 processed/                    # Legacy processed data
│   └── 📁 processed_improved/           # High-quality processed data
│
├── 📁 outputs/                          # Generated content
│   └── 📁 lesson_plans/                 # Generated lesson plans
│
└── 📁 docs/                             # Additional documentation
```

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Clone the repository
git clone https://github.com/Lakshit-Gupta/EduPlan_AI.git
cd EduPlan_AI

# Install dependencies
pip install -r requirements.txt

# Start Qdrant vector database (Docker required)
docker run -p 6333:6333 qdrant/qdrant
```

### 2. Initialize the System

```bash
# Setup the RAG pipeline (first time only)
python main.py setup

# Force rebuild if needed
python main.py setup --force
```

### 3. Generate Lesson Plans

```bash
# Basic lesson plan generation
python main.py generate "photosynthesis"

# Filtered by chapter
python main.py generate "atomic theory" --chapter "Chapter 3"

# Full specification
python main.py generate "evaporation" --chapter "Chapter 1" --subject "General"

# Check database status
python main.py check
```

## 🎯 Main.py Command Reference

### Command Structure
The main.py uses argparse with a hierarchical command structure:

```
main.py
├── setup       (subcommand)
│   └── --force (optional flag)
├── generate    (subcommand)
│   ├── topic   (positional argument - required)
│   ├── --chapter (optional filter)
│   └── --subject (optional, default='General')
└── check       (subcommand)
    └── (no additional arguments)
```

### Argument Types Explained

**Positional Arguments:**
- No `--` prefix required
- Order matters and usually required
- Example: `topic` in generate command

**Optional Arguments:**
- Require `--` prefix
- Order doesn't matter, can have defaults
- Example: `--chapter`, `--subject`

**Flags (Boolean):**
- `action='store_true'` means presence = True, absence = False
- No value required after the flag
- Example: `--force` in setup command

### Usage Examples

```bash
# Setup Commands
python main.py setup                     # Basic setup
python main.py setup --force             # Force rebuild

# Generation Commands  
python main.py generate "atomic theory"  # Basic generation
python main.py generate "photosynthesis" --chapter "Chapter 5"  # Chapter filter
python main.py generate "algebra" --subject "Mathematics"       # Subject filter

# Utility Commands
python main.py check                     # Database status
python main.py --help                   # Show help
python main.py generate --help          # Show generate help
```

### Argument Processing Flow

```python
# 1. Parse arguments
args = parser.parse_args()

# Example: python main.py generate "evaporation" --chapter "Chapter 1"
# Results in:
#   args.command = "generate"
#   args.topic = "evaporation"  
#   args.chapter = "Chapter 1"
#   args.subject = "General"    # default value

# 2. Route to handler
if args.command == 'setup':
    # Handle setup with optional --force
elif args.command == 'generate':
    # Handle generation with topic, chapter, subject
elif args.command == 'check':
    # Handle database status check
```

## 📊 System Architecture

```
📄 PDF Documents → 🔍 PyMuPDF Extraction → ✂️ Text Chunking → 🧠 nv-embed
                                                                    ↓
🎯 Query Input → 🤖 RAG Generator ← 💾 Qdrant Vector Database ← 📚 Improved Data
                        ↓
                📝 Lesson Plan Output
```

## 🛠️ Technical Specifications

### Core Components

**PDF Extraction (`scripts/improved_pdf_extractor.py`):**
- PyMuPDF-based text extraction
- Text cleaning to remove OCR artifacts
- Content type classification (headings, activities, questions)
- Structured JSON output with metadata

**Document Processing (`src/processors/improved_document_processor.py`):**
- Processes improved JSON format
- Sentence boundary-aware chunking
- Metadata preservation
- 818 high-quality chunks vs 381 legacy chunks

**Vector Database (`src/core/vector_database.py`):**
- Qdrant integration for similarity search
- Chapter and subject filtering
- Efficient batch operations
- 1024-dimensional embeddings

**Generation (`src/generators/lesson_plan_generator.py`):**
- RAG-based contextual generation
- Structured lesson plan templates
- Learning objectives and assessments
- Chapter-specific content retrieval

### Technical Details

- **Vector Database**: Qdrant (Docker-based)
- **Embedding Model**: NVIDIA nv-embed-text-latest (fallback: sentence-transformers)
- **Document Organization**: Chapter-wise categorization (Chapter 1-12)
- **Chunk Size**: 512 tokens with 50 token overlap
- **Vector Dimensions**: 1024 (nv-embed) / 384 (fallback)
- **Total Content**: 65,377 words across 12 chapters

## 📋 Configuration

Key settings in `src/core/config.py`:

```python
# Vector Database
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
QDRANT_VECTOR_SIZE = 1024

# Embedding Model
EMBEDDING_MODEL = "nvidia/nv-embed-text-latest"
FALLBACK_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Processing
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
BATCH_SIZE = 32
```

## 📝 Generated Output Example

```json
{
  "lesson_plan": {
    "title": "Atomic Theory and Molecular Structure",
    "chapter": "Chapter 3",
    "subject": "General",
    "duration": "45 minutes",
    "learning_objectives": [
      "Understand atomic structure fundamentals",
      "Explain molecular bonding concepts",
      "Apply Dalton's atomic theory"
    ],
    "key_concepts": [
      "Atomic structure and composition",
      "Chemical bonding principles", 
      "Molecular formation processes"
    ],
    "activities": [
      {
        "type": "Introduction",
        "duration": "10 minutes",
        "description": "Review atomic theory basics"
      }
    ],
    "assessment": {
      "formative": "Class discussion and Q&A",
      "summative": "Quiz on atomic structure"
    }
  }
}
```

## 🧪 Testing & Verification

```bash
# Check system status
python main.py check

# Verify database contents
python scripts/check_database.py

# Test lesson plan generation
python main.py generate "test topic" --chapter "Chapter 1"

# Compare extraction quality
python scripts/compare_extractions.py

# Analyze processed data
python scripts/analyze_json.py
```

## 📈 Performance Metrics

- **Document Processing**: 12 PDFs → 818 high-quality chunks
- **Embedding Generation**: Batch processing with progress tracking
- **Retrieval Speed**: Top-K results with similarity filtering
- **Memory Usage**: Optimized for educational content volume
- **Quality Score**: 65,377 clean words vs 32K garbled text

## 🔧 Advanced Usage

### Direct Script Usage

```bash
# Run improved pipeline directly
python scripts/run_improved_pipeline.py

# Extract PDFs with high quality
python scripts/improved_pdf_extractor.py

# Analyze extraction quality
python scripts/compare_extractions.py

# Check project structure
python scripts/show_project_structure.py
```

### Python API Usage

```python
from src.generators.lesson_plan_generator import LessonPlanGenerator

# Initialize generator
generator = LessonPlanGenerator()

# Generate lesson plan
lesson_plan = generator.generate_lesson_plan(
    query="atomic structure and chemical bonding",
    filter_chapter="Chapter 3",
    filter_subject="General"
)

print(lesson_plan)
```

## 🐛 Troubleshooting

### Common Issues

**Qdrant Connection Error:**
```bash
# Make sure Qdrant is running
docker run -p 6333:6333 qdrant/qdrant
```

**Poor Text Quality:**
```bash
# Use improved extraction pipeline
python scripts/run_improved_pipeline.py
```

**Missing Dependencies:**
```bash
pip install -r requirements.txt
```

**Empty Database:**
```bash
python main.py setup --force
```

## 🚧 Development

### File Organization
- **src/**: Core application modules with proper imports
- **scripts/**: Standalone utility scripts  
- **data/**: Raw PDFs and processed JSON files
- **outputs/**: Generated lesson plans and database

### Coding Standards
- Follow established directory structure
- Update imports when moving files
- Maintain consistent naming conventions
- Add appropriate docstrings and comments

## 🎯 Recent Improvements

### PDF Extraction Quality Fix ✅
- **Problem**: Garbled text with "MMMMM OOOOO SSSSS" artifacts from poor OCR
- **Solution**: PyMuPDF-based extraction with advanced text cleaning
- **Result**: 818 high-quality chunks vs 381 poor chunks (+115% improvement)

### Project Reorganization ✅
- **Before**: Scattered files in root directory
- **After**: Clean modular structure with proper separation of concerns
- **Benefits**: Better maintainability, clear architecture, professional layout

### Documentation & CLI ✅
- **Main Entry Point**: Comprehensive argument parsing system
- **Command Structure**: Intuitive setup/generate/check commands
- **User Guide**: Complete usage examples and troubleshooting

## 📄 License

See LICENSE file for details.

---

**Status**: ✅ **Production Ready** - High-quality PDF extraction, organized structure, comprehensive documentation

*EduPlan AI - Educational AI Platform* | *Generating the future of education, one lesson at a time* 🎓
