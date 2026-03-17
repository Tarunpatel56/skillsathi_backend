from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class GenerateQuizRequest(BaseModel):
    """Request to generate aptitude quiz questions."""
    topic: str = Field(..., description="Quiz topic: math, logic, verbal, data_interpretation")
    count: int = Field(5, ge=1, le=20, description="Number of questions")
    difficulty: str = Field("medium", description="Difficulty: easy / medium / hard")


class SubmitQuizRequest(BaseModel):
    """Submit answers for evaluation."""
    quiz_data: List[Dict] = Field(..., description="List of questions with user's answers")


class QuizQuestion(BaseModel):
    """Single quiz question."""
    id: int
    question: str
    options: Dict[str, str]
    correct_answer: str
    explanation: str
    topic: str


class QuizResponse(BaseModel):
    """Quiz generation response."""
    success: bool = True
    questions: List[Dict] = []
    topic: str = ""
    difficulty: str = ""


class QuizEvaluationResponse(BaseModel):
    """Quiz evaluation result."""
    success: bool = True
    total_questions: int = 0
    correct: int = 0
    wrong: int = 0
    score_percentage: float = 0.0
    weak_topics: List[str] = []
    recommendations: str = ""
