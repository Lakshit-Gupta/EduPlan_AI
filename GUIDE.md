# EduPlan_AI: Step-by-Step Guide

This guide will help you run the EduPlan_AI system from scratch.

## 1. Environment Setup

First, make sure you have the necessary dependencies:

```bash
pip install -r requirements.txt
```

## 2. Start the Vector Database

The system uses Qdrant as a vector database. Start it using Docker:

```bash
docker run -d -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

## 3. Process Educational Content

Run the data processing script to generate embeddings and store them in the database:

```bash
python src/scripts/process_improved_data.py
```

This script:
- Loads JSON files from the `data/processed_improved` directory
- Initializes the NV-Embed model
- Generates 4096-dimensional embeddings
- Stores the embeddings in the Qdrant database

## 4. Generate Lesson Plans

Run the pipeline script to generate lesson plans:

```bash
python scripts/run_improved_pipeline.py
```

This will:
- Check the Qdrant database connection
- Generate lesson plans for example topics
- Save the lesson plans to `outputs/lesson_plans`

## 5. Examine the Results

The generated lesson plans are stored as JSON files in the `outputs/lesson_plans` directory. You can open these files to see the structured lesson plans.

## 6. Customize for Your Needs

To generate lesson plans for your own topics:

1. Edit the `example_topics` list in `scripts/run_improved_pipeline.py`
2. Run the script again

## Troubleshooting

- If you get errors about the database connection, make sure the Qdrant container is running
- If the embedding generation fails, ensure you have enough GPU memory available
- If no results are returned, check that your data files are in the correct format and location
