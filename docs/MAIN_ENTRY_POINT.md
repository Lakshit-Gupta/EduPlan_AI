# 🔧 EduPlan AI - Main Entry Point & Argument Parsing

## 📋 **Overview**

The `main.py` file serves as the central command-line interface for the EduPlan AI platform. It uses Python's `argparse` library to provide a user-friendly way to interact with the system through different commands and options.

## 🏗️ **Updated Project Structure**

```
EduPlan_AI/
├── 📁 src/                          # Source code (organized modules)
│   ├── 📁 core/                     # Core components
│   │   ├── config.py                # Central configuration
│   │   ├── vector_database.py       # Qdrant database connector
│   │   └── __init__.py
│   ├── 📁 models/                   # AI/ML Models  
│   │   ├── embedding_model.py       # NVIDIA nv-embed + fallback
│   │   └── __init__.py
│   ├── 📁 processors/               # Data processors
│   │   ├── document_processor.py    # Legacy processor
│   │   ├── improved_document_processor.py  # New high-quality processor
│   │   └── __init__.py
│   ├── 📁 generators/               # Content generators
│   │   ├── lesson_plan_generator.py # RAG-based lesson plan generator
│   │   └── __init__.py
│   └── 📁 api/                      # Web API (Flask)
│       └── app.py                   # Flask application
├── 📁 scripts/                      # Executable scripts & utilities
│   ├── run_mvp_pipeline.py          # Original pipeline
│   ├── run_improved_pipeline.py     # Improved pipeline (recommended)
│   ├── improved_pdf_extractor.py    # High-quality PDF extraction
│   ├── check_database.py            # Database status checker
│   ├── analyze_json.py              # JSON analysis tools
│   ├── compare_extractions.py       # Quality comparison
│   ├── check_lesson_quality.py      # Lesson plan quality checker
│   └── 📁 legacy/                   # Old/deprecated scripts
├── 📁 data/                         # Data storage
│   ├── 📁 raw/                      # Raw PDF files (12 chapters)
│   ├── 📁 processed/                # Legacy JSON extraction
│   └── 📁 processed_improved/       # High-quality JSON (recommended)
├── 📁 outputs/                      # Generated content
│   └── 📁 lesson_plans/             # Generated lesson plans
├── 📁 docs/                         # Documentation & project files
├── 📁 tests/                        # Test files
├── 📁 analysis_tool/                # Analysis utilities
├── 📁 common/                       # Shared utilities  
├── 📁 exam_creator/                 # Exam generation tools
├── 📁 homework_creator/             # Homework generation tools
├── 📁 lesson_plan/                  # Lesson plan utilities
├── main.py                          # 🎯 MAIN ENTRY POINT
├── requirements.txt                 # Python dependencies
└── README.md                        # Project documentation
```

## 🎯 **Main.py Argument Parsing Explained**

### **1. Argument Parser Setup**

```python
import argparse

def main():
    parser = argparse.ArgumentParser(description='EduPlan AI - Educational AI Platform')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
```

**What this does:**
- Creates the main argument parser with a description
- Sets up subcommands using `subparsers` for different operations
- `dest='command'` stores the chosen subcommand in `args.command`

### **2. Available Commands**

#### **🚀 Setup Command**
```python
setup_parser = subparsers.add_parser('setup', help='Set up the RAG pipeline')
setup_parser.add_argument('--force', action='store_true', help='Force rebuild of database')
```

**Usage:** `python main.py setup [--force]`
- **Purpose:** Initialize the RAG pipeline and vector database
- **`--force` flag:** Optional flag to force rebuild even if database exists
- **What it does:** Runs the pipeline setup script

#### **📝 Generate Command**
```python
generate_parser = subparsers.add_parser('generate', help='Generate lesson plan')
generate_parser.add_argument('topic', help='Lesson plan topic')
generate_parser.add_argument('--chapter', help='Filter by chapter (e.g., Chapter 3)')
generate_parser.add_argument('--subject', default='General', help='Filter by subject')
```

**Usage:** `python main.py generate "topic" --chapter "Chapter 3" --subject "General"`

**Parameters Breakdown:**
- **`topic`** (positional, required): The lesson plan topic/query
- **`--chapter`** (optional): Filter search to specific chapter
- **`--subject`** (optional, default='General'): Filter by subject category

#### **🔍 Check Command**
```python
check_parser = subparsers.add_parser('check', help='Check database status')
```

**Usage:** `python main.py check`
- **Purpose:** Check vector database status and contents
- **What it shows:** Document count, chapters available, sample content

### **3. Command Processing Logic**

```python
args = parser.parse_args()

if args.command == 'setup':
    print("🚀 Running EduPlan AI Setup...")
    os.system('python scripts/run_mvp_pipeline.py')
    
elif args.command == 'generate':
    print(f"📝 Generating lesson plan for: {args.topic}")
    from src.generators.lesson_plan_generator import LessonPlanGenerator
    
    generator = LessonPlanGenerator()
    lesson_plan = generator.generate_lesson_plan(
        query=args.topic,
        filter_chapter=args.chapter,
        filter_subject=args.subject
    )
    
    # Save lesson plan
    import json
    filename = f"lesson_plan_{args.topic.replace(' ', '_').lower()}.json"
    output_path = os.path.join('outputs/lesson_plans', filename)
    
    with open(output_path, 'w') as f:
        json.dump(lesson_plan, f, indent=2)
        
    print(f"✅ Lesson plan saved to: {output_path}")
    
elif args.command == 'check':
    print("🔍 Checking database status...")
    os.system('python scripts/check_database.py')
    
else:
    parser.print_help()
```

## 🔄 **Detailed Flow for Generate Command**

### **Example:** `python main.py generate "Evaporation" --chapter "Chapter 1" --subject "General"`

**Step-by-Step Execution:**

1. **Argument Parsing:**
   ```python
   args.command = "generate"
   args.topic = "Evaporation"
   args.chapter = "Chapter 1"
   args.subject = "General"
   ```

2. **Import Components:**
   ```python
   from src.generators.lesson_plan_generator import LessonPlanGenerator
   ```

3. **Initialize Generator:**
   ```python
   generator = LessonPlanGenerator()
   # This loads:
   # - Qdrant database connection
   # - Embedding model (nv-embed + fallback)
   # - Configuration from src/core/config.py
   ```

4. **Generate Lesson Plan:**
   ```python
   lesson_plan = generator.generate_lesson_plan(
       query="Evaporation",           # Search term
       filter_chapter="Chapter 1",    # Chapter filter
       filter_subject="General"       # Subject filter
   )
   ```

5. **Internal Processing:**
   - Convert query to embedding vector
   - Search Qdrant database with filters
   - Retrieve top 5 relevant documents
   - Generate structured lesson plan using RAG

6. **Save Output:**
   ```python
   filename = "lesson_plan_evaporation.json"
   output_path = "outputs/lesson_plans/lesson_plan_evaporation.json"
   ```

## 🎛️ **Configuration Integration**

The main.py file integrates with `src/core/config.py` for:

```python
# From config.py
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
EMBEDDING_MODEL = "nvidia/nv-embed-text-latest"
FALLBACK_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 512
TOP_K_RESULTS = 5
OUTPUT_DIR = "outputs/lesson_plans"
```

## 🚀 **Usage Examples**

### **Basic Setup:**
```bash
python main.py setup
```

### **Generate Lesson Plans:**
```bash
# Basic generation
python main.py generate "photosynthesis"

# With chapter filter
python main.py generate "atomic structure" --chapter "Chapter 3"

# With both filters
python main.py generate "evaporation" --chapter "Chapter 1" --subject "General"
```

### **Check System Status:**
```bash
python main.py check
```

### **Help Information:**
```bash
python main.py --help           # Main help
python main.py generate --help  # Generate command help
```

## 🔍 **Error Handling**

The system includes several error handling mechanisms:
- **Missing arguments:** argparse automatically shows usage help
- **Invalid commands:** Falls back to showing help
- **Import errors:** Shows clear error messages for missing dependencies
- **Database errors:** Provides troubleshooting guidance

## 🛠️ **Advanced Usage**

For more advanced operations, you can also run scripts directly:

```bash
# Use improved pipeline (recommended)
python scripts/run_improved_pipeline.py

# Check lesson quality
python scripts/check_lesson_quality.py

# Analyze data structure
python scripts/analyze_json.py
```

This architecture provides a clean, extensible command-line interface while maintaining separation of concerns between the entry point and the underlying components.
