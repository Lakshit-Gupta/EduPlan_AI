from typing import List, Dict, Any
import sys
import os
import json
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from retrieval.retriever import DocumentRetriever

class LessonPlanGenerator:
    """
    Generate lesson plans based on retrieved documents and user queries
    """
    
    def __init__(self, model_name: str = None):
        """
        Initialize the lesson plan generator
        
        Args:
            model_name: Name of the language model to use
        """
        self.model_name = model_name or config.MODEL_NAME
        self.retriever = DocumentRetriever()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        try:
            # Load model and tokenizer for generation
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name).to(self.device)
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Using a simplified mock generator for development")
            self.tokenizer = None
            self.model = None
    
    def _create_prompt(self, query: str, context_docs: List[Dict[str, Any]]) -> str:
        """
        Create a prompt for the language model
        
        Args:
            query: User query
            context_docs: Retrieved documents
            
        Returns:
            Formatted prompt string
        """
        # Extract relevant context from documents
        context = "\n\n".join([doc["text"] for doc in context_docs])
        
        # Format class and subject information
        class_info = "unknown"
        subject_info = "unknown"
        
        if context_docs:
            class_info = context_docs[0].get("class", "unknown")
            subject_info = context_docs[0].get("subject", "unknown")
        
        # Create the prompt
        prompt = f"""
Task: Create a detailed lesson plan based on the following information.

Class: {class_info}
Subject: {subject_info}
Request: {query}

Reference Material:
{context}

Generate a comprehensive lesson plan with the following sections:
1. Learning Objectives (3-5 specific objectives)
2. Key Concepts (main ideas to cover)
3. Teaching Materials (resources needed)
4. Lesson Structure:
   - Introduction (5-7 minutes)
   - Main Activities (20-30 minutes)
   - Practice (10-15 minutes)
   - Assessment (5-10 minutes)
   - Conclusion (3-5 minutes)
5. Homework/Extension Activities
6. Assessment Strategies

Lesson Plan:
"""
        return prompt
    
    def _generate_with_model(self, prompt: str) -> str:
        """
        Generate text using the language model
        
        Args:
            prompt: Input prompt
            
        Returns:
            Generated text
        """
        if not self.model or not self.tokenizer:
            # Mock generation for development
            return self._mock_generate(prompt)
        
        # Tokenize prompt
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        
        # Generate
        outputs = self.model.generate(
            inputs["input_ids"],
            max_length=2048,
            temperature=config.TEMPERATURE,
            num_return_sequences=1,
            do_sample=True,
            top_p=0.95
        )
        
        # Decode and return
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract the generated part (after the prompt)
        return generated_text[len(prompt):]
    
    def _mock_generate(self, prompt: str) -> str:
        """
        Mock generation for development without actual model
        
        Args:
            prompt: Input prompt
            
        Returns:
            Template-based mock output
        """
        # Extract class and subject from prompt
        class_match = prompt.find("Class: ") 
        class_end = prompt.find("\n", class_match)
        class_info = prompt[class_match + 7:class_end].strip()
        
        subject_match = prompt.find("Subject: ")
        subject_end = prompt.find("\n", subject_match)
        subject_info = prompt[subject_match + 9:subject_end].strip()
        
        # Basic template response
        return f"""
## Learning Objectives
- Students will understand key concepts in {subject_info} for class {class_info}
- Students will be able to apply these concepts to solve problems
- Students will develop critical thinking skills related to the topic

## Key Concepts
- Core principles of {subject_info} at class {class_info} level
- Application of concepts to real-world scenarios
- Problem-solving strategies

## Teaching Materials
- Textbook
- Worksheets
- Visual aids
- Digital resources

## Lesson Structure

### Introduction (5-7 minutes)
- Begin with an engaging question to spark interest
- Connect to previous knowledge
- Outline learning objectives for the class

### Main Activities (20-30 minutes)
- Present new concepts with examples
- Guided practice with teacher support
- Interactive demonstrations

### Practice (10-15 minutes)
- Independent work on exercises
- Pair/group work on application problems
- Differentiated tasks for various learning levels

### Assessment (5-10 minutes)
- Quick formative assessment
- Exit ticket or concept check
- Group sharing of solutions

### Conclusion (3-5 minutes)
- Summarize key learnings
- Preview next lesson
- Answer any remaining questions

## Homework/Extension Activities
- Practice problems from textbook
- Research project on real-world applications
- Preparation reading for next lesson

## Assessment Strategies
- Formative assessment during class activities
- Homework completion and accuracy
- Quiz on concepts in next class
- Project-based assessment
"""
    
    def generate_lesson_plan(
        self, 
        query: str, 
        class_filter: str = None,
        subject_filter: str = None,
        num_context_docs: int = None
    ) -> Dict[str, Any]:
        """
        Generate a lesson plan based on a query
        
        Args:
            query: User query for lesson plan
            class_filter: Optional class filter
            subject_filter: Optional subject filter
            num_context_docs: Number of documents to retrieve for context
            
        Returns:
            Generated lesson plan with metadata
        """
        if num_context_docs is None:
            num_context_docs = config.TOP_K_RESULTS
        
        # Retrieve relevant documents
        context_docs = self.retriever.retrieve(
            query=query,
            top_k=num_context_docs,
            filter_class=class_filter,
            filter_subject=subject_filter
        )
        
        # Create prompt
        prompt = self._create_prompt(query, context_docs)
        
        # Generate lesson plan
        generated_text = self._generate_with_model(prompt)
        
        # Prepare response with metadata
        response = {
            "lesson_plan": generated_text,
            "metadata": {
                "query": query,
                "class": class_filter or (context_docs[0].get("class") if context_docs else "unknown"),
                "subject": subject_filter or (context_docs[0].get("subject") if context_docs else "unknown"),
                "sources": [
                    {
                        "filename": doc.get("filename"),
                        "relevance_score": doc.get("score"),
                        "class": doc.get("class"),
                        "subject": doc.get("subject"),
                        "topic": doc.get("topic")
                    } 
                    for doc in context_docs
                ],
                "num_sources": len(context_docs)
            }
        }
        
        return response
