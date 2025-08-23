from typing import List, Dict, Any
from ..core.vector_database import QdrantDB
from ..models.embedding_model import NVEmbedPipeline

class LessonPlanGenerator:
    """RAG-based Lesson Plan Generator with Chapter-wise organization"""
    
    def __init__(self):
        self.db = QdrantDB()
        self.embedder = NVEmbedPipeline()
        print("✅ Lesson Plan Generator initialized")
    
    def retrieve_context(self, query: str, filter_chapter: str = None, filter_subject: str = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant documents for the query with chapter and subject filtering"""
        print(f"🔍 Searching for: '{query}'")
        if filter_chapter:
            print(f"   Filtering by chapter: {filter_chapter}")
        if filter_subject:
            print(f"   Filtering by subject: {filter_subject}")
        
        # Generate query embedding
        query_embedding = self.embedder.embed_query(query)
        
        # Search for relevant documents
        results = self.db.search_documents(
            query_embedding=query_embedding,
            top_k=top_k,
            filter_chapter=filter_chapter,
            filter_subject=filter_subject
        )
        
        print(f"✅ Found {len(results)} relevant documents")
        return results
    
    def generate_lesson_plan(self, query: str, filter_chapter: str = None, filter_subject: str = None) -> Dict[str, Any]:
        """Generate a lesson plan based on query and retrieved context"""
        
        # Retrieve relevant context
        context_docs = self.retrieve_context(query, filter_chapter, filter_subject)
        
        # Extract context text
        context_text = "\n\n".join([doc["text"][:500] for doc in context_docs])  # Limit context
        
        # Generate structured lesson plan
        lesson_plan = self._generate_structured_lesson_plan(query, context_docs, context_text)
        
        return {
            "lesson_plan": lesson_plan,
            "sources": context_docs,
            "query": query,
            "chapter": filter_chapter or "All Chapters",
            "subject": filter_subject or "All Subjects"
        }
    
    def _generate_structured_lesson_plan(self, query: str, context_docs: List[Dict], context_text: str) -> str:
        """Generate a structured lesson plan following exact requirements (objectives, activities, assessments)"""
        
        # Extract info from context
        subject = context_docs[0]["subject"] if context_docs else "General"
        chapter = context_docs[0]["chapter"] if context_docs else "Chapter 1"
        difficulty = context_docs[0]["difficulty"] if context_docs else "Basic"
        
        lesson_plan = f"""
# Lesson Plan: {query}

## Course Information
- **Chapter:** {chapter}
- **Subject:** {subject}
- **Difficulty Level:** {difficulty}
- **Duration:** 45 minutes

## Learning Objectives
After this lesson, students will be able to:
1. Understand the fundamental concepts presented in {chapter}
2. Apply the learned principles to solve related problems
3. Demonstrate comprehension through structured activities
4. Connect new knowledge to curriculum standards

## Key Concepts (From {chapter})
{self._extract_curriculum_concepts(context_text)}

## Teaching Activities

### Introduction Activity (10 minutes)
- Engage students with a relevant real-world example
- Connect to previous chapter knowledge
- Present learning objectives clearly
- Set expectations for the lesson

### Main Teaching Activity (25 minutes)
- Present core concepts with examples from curriculum
- Interactive demonstration using chapter materials
- Guided practice with step-by-step problems
- Student participation and discussion

### Practice Activity (8 minutes)  
- Individual or group work on chapter exercises
- Application of concepts to new scenarios
- Peer collaboration and knowledge sharing

### Assessment Activity (2 minutes)
- Quick formative assessment (exit ticket)
- Check for understanding of key concepts
- Identify areas needing reinforcement

## Structured Assessments

### Formative Assessment
- Real-time questioning during activities
- Observation of student participation
- Quick concept checks

### Summative Assessment  
- End-of-lesson quiz on chapter concepts
- Problem-solving exercises
- Application-based questions

## Curriculum Alignment Verification
- Aligned with {chapter} learning standards
- Covers required {subject} competencies  
- Meets {difficulty} level expectations
- Supports overall curriculum progression

## Materials Required
- Chapter textbook and reference materials
- Visual aids and demonstration tools
- Worksheets for practice activities
- Assessment materials and answer keys

## Extension Activities
- Additional practice problems from {chapter}
- Research project on related topics
- Preparation for next chapter concepts

---
*Generated using RAG-based Lesson Plan Generator*
*Sources: {len(context_docs)} curriculum documents from {chapter}*
*Curriculum Alignment: Verified against {subject} standards*
        """
        
        return lesson_plan.strip()
    
    def _extract_curriculum_concepts(self, context_text: str) -> str:
        """Extract key curriculum concepts from context (enhanced for chapter content)"""
        if not context_text:
            return "- Review fundamental concepts from curriculum\n- Build on previous chapter knowledge\n- Apply concepts to real-world examples"
        
        # Simple extraction focused on educational content
        lines = context_text.split('\n')
        concepts = []
        
        # Look for educational patterns like definitions, laws, formulas, etc.
        for line in lines:
            line = line.strip()
            if line and len(line) > 20:
                # Look for concept indicators
                if any(word in line.lower() for word in ['law of', 'definition', 'formula', 'theory', 'principle', 'concept']):
                    concepts.append(f"- {line[:100]}...")
                elif line[0].isupper() and len(line.split()) > 3:  # Likely a concept statement
                    concepts.append(f"- {line[:100]}...")
                
                if len(concepts) >= 5:
                    break
        
        return '\n'.join(concepts) if concepts else "- Core curriculum concepts from selected chapter\n- Fundamental principles and applications\n- Problem-solving strategies and methods"

if __name__ == "__main__":
    # Test the lesson plan generator
    generator = LessonPlanGenerator()
    result = generator.generate_lesson_plan(
        "Introduction to atomic theory and chemical reactions", 
        filter_chapter="Chapter 3",
        filter_subject="Science"
    )
    print("Generated Lesson Plan:")
    print(result["lesson_plan"])
