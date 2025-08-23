# Exam Creator MVP - Day 2
# TODO: Implement MCQ-based exam generation with topic, difficulty, and score inputs

class ExamCreator:
    """
    MVP for creating simple MCQ-based exams
    Features planned:
    - Template-based MCQs
    - Auto-scoring and percentage calculation  
    - JSON-based output
    """
    
    def __init__(self):
        """Initialize the exam creator"""
        pass
    
    def create_exam(self, topic: str, difficulty: str, num_questions: int = 10):
        """
        Create an exam based on topic and difficulty
        
        Args:
            topic: Subject topic for the exam
            difficulty: Difficulty level (easy, medium, hard)
            num_questions: Number of questions to generate
            
        Returns:
            Dict containing exam questions and metadata
        """
        # Placeholder for Day 2 implementation
        return {
            "exam_id": "placeholder",
            "topic": topic,
            "difficulty": difficulty,
            "questions": [],
            "total_questions": num_questions,
            "status": "pending_implementation"
        }
