EduRAG: AI-Powered Lesson Plan Generation

EduRAG is an intelligent educational platform that leverages Retrieval-Augmented Generation (RAG) to automate lesson plan creation for classes 1–12. The system organizes curriculum documents, embeds them using NVIDIA nv-embed, and stores them in Qdrant for efficient semantic search. Teachers and students can query the system to generate curriculum-aligned lesson plans with structured objectives, activities, and assessments.

 Key Features:

Class-wise curriculum document management

Metadata tagging (subject, chapter, difficulty)

Semantic search with similarity scoring

Context-aware lesson plan generation

Curriculum alignment verification

API for easy integration into learning platforms

🛠️ Tech Stack:

Database: Qdrant (vector database)

Embeddings: NVIDIA nv-embed

Architecture: RAG (Retrieve → Rank → Generate)

Frameworks: Python, FastAPI

 MVP Goal: Set up Qdrant, build a document ingestion + embedding pipeline, and generate simple lesson plan templates from retrieved documents.
