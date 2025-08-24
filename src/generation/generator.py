from typing import Dict, Any, List
import json
import os
from datetime import datetime
from ..core.config import LLM_MODEL, LLM_API_KEY, LLM_BASE_URL
from ..retrieval.retriever import DocumentRetriever

class LessonPlanGenerator:
    """
    Advanced lesson plan generator using RAG and LLM
    """
    
    def __init__(self):
        """Initialize the generator with retriever and LLM client"""
        self.retriever = DocumentRetriever()
        self.client = None
        self.setup_llm_client()
        print("🎓 Lesson plan generator initialized")
    
    def setup_llm_client(self):
        """Setup the LLM client (OpenAI, Groq, or local)"""
        try:
            if "groq" in LLM_BASE_URL.lower():
                from groq import Groq
                self.client = Groq(api_key=LLM_API_KEY)
                print(f"🚀 Connected to Groq LLM: {LLM_MODEL}")
            else:
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=LLM_API_KEY,
                    base_url=LLM_BASE_URL if LLM_BASE_URL != "https://api.openai.com/v1" else None
                )
                print(f"🤖 Connected to OpenAI-compatible LLM: {LLM_MODEL}")
        except Exception as e:
            print(f"❌ Error setting up LLM client: {str(e)}")
            raise
    
    def generate_lesson_plan(
        self,
        topic: str,
        chapter: str = None,
        subject: str = "General",
        grade_level: str = "Middle School",
        duration: int = 45,
        learning_objectives: List[str] = None,
        output_format: str = "json"
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive lesson plan
        
        Args:
            topic: Main topic of the lesson
            chapter: Optional chapter context
            subject: Subject area
            grade_level: Target grade level
            duration: Lesson duration in minutes
            learning_objectives: Optional specific objectives
            output_format: Output format (json, text, or markdown)
            
        Returns:
            Generated lesson plan as dictionary
        """
        print(f"🎯 Generating lesson plan for: '{topic}' (Subject: {subject}, Chapter: {chapter})")
        
        # Retrieve relevant context
        context = self.retriever.retrieve_context_for_generation(
            topic=topic,
            subject=subject,
            chapter=chapter,
            top_k=6  # Get more context for better generation
        )
        
        # Create the generation prompt
        prompt = self.create_lesson_plan_prompt(
            topic=topic,
            chapter=chapter,
            subject=subject,
            grade_level=grade_level,
            duration=duration,
            learning_objectives=learning_objectives,
            context=context
        )
        
        try:
            # Generate lesson plan using LLM
            response = self.client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert educational content designer specializing in creating comprehensive, engaging lesson plans. Use the provided educational context to create detailed, practical lesson plans that follow best pedagogical practices."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            lesson_plan_text = response.choices[0].message.content
            
            # Parse and structure the lesson plan
            lesson_plan = self.parse_lesson_plan(
                lesson_plan_text=lesson_plan_text,
                topic=topic,
                chapter=chapter,
                subject=subject,
                grade_level=grade_level,
                duration=duration
            )
            
            print(f"✅ Successfully generated lesson plan for '{topic}'")
            return lesson_plan
            
        except Exception as e:
            print(f"❌ Error generating lesson plan: {str(e)}")
            raise
    
    def create_lesson_plan_prompt(
        self,
        topic: str,
        chapter: str,
        subject: str,
        grade_level: str,
        duration: int,
        learning_objectives: List[str],
        context: str
    ) -> str:
        """Create the prompt for lesson plan generation"""
        
        objectives_text = ""
        if learning_objectives:
            objectives_text = f"Specific Learning Objectives:\n" + "\n".join([f"- {obj}" for obj in learning_objectives])
        
        prompt = f"""
Create a comprehensive lesson plan based on the following requirements and educational context:

LESSON REQUIREMENTS:
- Topic: {topic}
- Subject: {subject}
- Chapter: {chapter or 'Not specified'}
- Grade Level: {grade_level}
- Duration: {duration} minutes
{objectives_text}

EDUCATIONAL CONTEXT:
{context}

Please create a detailed lesson plan that includes:

1. LESSON OVERVIEW
   - Clear lesson title
   - Brief description
   - Key learning outcomes

2. LEARNING OBJECTIVES
   - 3-5 specific, measurable objectives
   - Aligned with the topic and educational context

3. MATERIALS NEEDED
   - List of required materials and resources
   - Technology requirements if any

4. LESSON STRUCTURE (with time allocations)
   - Introduction/Hook (5-10 minutes)
   - Main Content Delivery (20-25 minutes)
   - Activities/Practice (10-15 minutes)
   - Assessment/Wrap-up (5-10 minutes)

5. DETAILED ACTIVITIES
   - Step-by-step instructions for each activity
   - Student engagement strategies
   - Differentiation considerations

6. ASSESSMENT METHODS
   - Formative assessment strategies
   - Summative assessment options
   - Success criteria

7. EXTENSION ACTIVITIES
   - Additional activities for advanced learners
   - Real-world connections
   - Cross-curricular links

8. RESOURCES AND REFERENCES
   - Additional reading materials
   - Online resources
   - Related educational content

Format the response as a well-structured lesson plan that a teacher can immediately implement. Use the educational context provided to ensure accuracy and relevance.
"""
        return prompt
    
    def parse_lesson_plan(
        self,
        lesson_plan_text: str,
        topic: str,
        chapter: str,
        subject: str,
        grade_level: str,
        duration: int
    ) -> Dict[str, Any]:
        """Parse and structure the generated lesson plan"""
        
        # Create structured lesson plan
        lesson_plan = {
            "metadata": {
                "title": f"Lesson Plan: {topic}",
                "topic": topic,
                "chapter": chapter,
                "subject": subject,
                "grade_level": grade_level,
                "duration_minutes": duration,
                "generated_at": datetime.now().isoformat(),
                "generator": "EduPlan AI - RAG-Enhanced Generator"
            },
            "content": {
                "full_lesson_plan": lesson_plan_text,
                "structured_sections": self.extract_sections(lesson_plan_text)
            },
            "quality_metrics": {
                "content_length": len(lesson_plan_text),
                "estimated_reading_time": len(lesson_plan_text.split()) // 200,  # Approximate reading time
                "section_count": len(self.extract_sections(lesson_plan_text))
            }
        }
        
        return lesson_plan
    
    def extract_sections(self, text: str) -> Dict[str, str]:
        """Extract different sections from the lesson plan text"""
        sections = {}
        
        # Common section headers to look for
        section_headers = [
            "LESSON OVERVIEW", "LEARNING OBJECTIVES", "MATERIALS NEEDED",
            "LESSON STRUCTURE", "DETAILED ACTIVITIES", "ASSESSMENT METHODS",
            "EXTENSION ACTIVITIES", "RESOURCES AND REFERENCES"
        ]
        
        current_section = "introduction"
        current_content = []
        
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Check if line is a section header
            header_found = False
            for header in section_headers:
                if header.lower() in line.lower() and len(line) < 100:
                    # Save previous section
                    if current_content:
                        sections[current_section] = '\n'.join(current_content).strip()
                    
                    # Start new section
                    current_section = header.lower().replace(' ', '_')
                    current_content = []
                    header_found = True
                    break
            
            if not header_found and line:
                current_content.append(line)
        
        # Save final section
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def save_lesson_plan(self, lesson_plan: Dict[str, Any], output_dir: str = "outputs/lesson_plans") -> str:
        """Save the lesson plan to a file"""
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename
        topic_clean = lesson_plan["metadata"]["topic"].lower().replace(" ", "_").replace("/", "_")
        filename = f"lesson_plan_{topic_clean}.json"
        filepath = os.path.join(output_dir, filename)
        
        # Save as JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(lesson_plan, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Lesson plan saved to: {filepath}")
        return filepath
    
    def generate_and_save(
        self,
        topic: str,
        chapter: str = None,
        subject: str = "General",
        grade_level: str = "Middle School",
        duration: int = 45,
        learning_objectives: List[str] = None
    ) -> str:
        """Generate and save a lesson plan in one step"""
        
        lesson_plan = self.generate_lesson_plan(
            topic=topic,
            chapter=chapter,
            subject=subject,
            grade_level=grade_level,
            duration=duration,
            learning_objectives=learning_objectives
        )
        
        filepath = self.save_lesson_plan(lesson_plan)
        return filepath

if __name__ == "__main__":
    # Test the generator
    generator = LessonPlanGenerator()
    
    # Generate a test lesson plan
    lesson_plan = generator.generate_lesson_plan(
        topic="Evaporation and Water Cycle",
        chapter="Chapter 1",
        subject="Science",
        grade_level="6th Grade",
        duration=45
    )
    
    print(f"Generated lesson plan: {lesson_plan['metadata']['title']}")
    print(f"Content length: {lesson_plan['quality_metrics']['content_length']} characters")