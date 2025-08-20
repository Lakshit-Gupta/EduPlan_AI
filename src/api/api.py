from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import sys
import tempfile
from typing import List, Dict, Any, Optional
import shutil
from pydantic import BaseModel

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from ingestion_pipeline import DocumentIngestionPipeline
from generation.generator import LessonPlanGenerator

app = FastAPI(
    title="EduPlan AI - Lesson Plan Generator",
    description="An AI system for generating curriculum-aligned lesson plans",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
ingestion_pipeline = DocumentIngestionPipeline()
lesson_plan_generator = LessonPlanGenerator()

# Models for request validation
class LessonPlanRequest(BaseModel):
    query: str
    class_filter: Optional[str] = None
    subject_filter: Optional[str] = None
    num_context_docs: Optional[int] = None

class DocumentMetadata(BaseModel):
    class_number: str
    subject: str
    topic: str
    difficulty: Optional[str] = "basic"

@app.get("/")
def read_root():
    return {"message": "Welcome to EduPlan AI - Lesson Plan Generator API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/upload-document")
async def upload_document(
    file: UploadFile = File(...),
    class_number: str = Form(...),
    subject: str = Form(...),
    topic: str = Form(...),
    difficulty: str = Form("basic")
):
    # Validate file extension
    file_extension = file.filename.split(".")[-1]
    if file_extension not in config.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Allowed formats: {config.ALLOWED_EXTENSIONS}"
        )
    
    # Validate class
    if class_number not in config.CLASS_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid class number. Allowed values: {config.CLASS_CATEGORIES}"
        )
    
    # Save file to temp directory
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_file_path = temp_file.name
    
    try:
        # Process and ingest document
        doc_ids, metadata = ingestion_pipeline.ingest_file(temp_file_path)
        
        return {
            "message": "Document uploaded and processed successfully",
            "document_ids": doc_ids,
            "chunks": len(doc_ids),
            "metadata": {
                "filename": file.filename,
                "class": class_number,
                "subject": subject,
                "topic": topic,
                "difficulty": difficulty
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )
    finally:
        # Clean up temp file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

@app.post("/generate-lesson-plan")
def generate_lesson_plan(request: LessonPlanRequest):
    try:
        # Generate lesson plan
        response = lesson_plan_generator.generate_lesson_plan(
            query=request.query,
            class_filter=request.class_filter,
            subject_filter=request.subject_filter,
            num_context_docs=request.num_context_docs
        )
        
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating lesson plan: {str(e)}"
        )

@app.get("/classes")
def get_classes():
    return {"classes": config.CLASS_CATEGORIES}

# Main function to run the API
def main():
    uvicorn.run(
        "api:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=config.DEBUG
    )

if __name__ == "__main__":
    main()
