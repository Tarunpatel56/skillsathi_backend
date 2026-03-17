"""
Aptitude & Quiz Endpoints – Quiz generation, submission, and evaluation.
"""
from fastapi import APIRouter, Depends, HTTPException
from models.aptitude_models import (
    GenerateQuizRequest, QuizResponse,
    SubmitQuizRequest, QuizEvaluationResponse,
)
from core.prompts import (
    APTITUDE_MASTER_SYSTEM,
    GENERATE_QUIZ_PROMPT,
    EVALUATE_QUIZ_PROMPT,
)
from api.deps import get_groq_service
from services.groq_service import GroqService
import json

router = APIRouter(prefix="/aptitude", tags=["Aptitude & Quizzes"])


@router.post("/generate-quiz")
async def generate_quiz(
    req: GenerateQuizRequest,
    groq: GroqService = Depends(get_groq_service),
):
    """Generate aptitude quiz questions based on topic and difficulty."""
    try:
        prompt = GENERATE_QUIZ_PROMPT.format(
            count=req.count,
            topic=req.topic,
            difficulty=req.difficulty,
        )
        result = await groq.chat_json(APTITUDE_MASTER_SYSTEM, prompt)
        return {
            "success": True,
            "topic": req.topic,
            "difficulty": req.difficulty,
            "questions": result if isinstance(result, list) else result.get("questions", result),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submit-quiz")
async def submit_quiz(
    req: SubmitQuizRequest,
    groq: GroqService = Depends(get_groq_service),
):
    """Submit quiz answers and get performance evaluation."""
    try:
        prompt = EVALUATE_QUIZ_PROMPT.format(
            quiz_data=json.dumps(req.quiz_data, indent=2),
        )
        result = await groq.chat_json(APTITUDE_MASTER_SYSTEM, prompt)
        return {"success": True, "evaluation": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/topics")
async def get_topics():
    """Get available aptitude quiz topics."""
    return {
        "success": True,
        "topics": [
            {"id": "math", "name": "Mathematics", "description": "Arithmetic, Algebra, Geometry, Percentages"},
            {"id": "logic", "name": "Logical Reasoning", "description": "Puzzles, Patterns, Sequences, Deductions"},
            {"id": "verbal", "name": "Verbal Ability", "description": "Synonyms, Antonyms, Reading Comprehension, Analogies"},
            {"id": "data_interpretation", "name": "Data Interpretation", "description": "Tables, Charts, Graphs, Data Analysis"},
            {"id": "general_knowledge", "name": "General Knowledge", "description": "Current Affairs, Science, History, Geography"},
        ],
    }
