"""
Interview Preparation Endpoints – Mock interviews & answer evaluation.
"""
from fastapi import APIRouter, Depends, HTTPException
from models.interview_models import (
    StartInterviewRequest, AnswerRequest,
    InterviewResponse, CommonQuestionsRequest,
)
from core.prompts import (
    INTERVIEW_COACH_SYSTEM,
    MOCK_INTERVIEW_PROMPT,
    ANSWER_EVALUATION_PROMPT,
)
from api.deps import get_groq_service
from services.groq_service import GroqService, GroqServiceError

router = APIRouter(prefix="/interview", tags=["Interview Prep"])


@router.post("/start")
async def start_interview(
    req: StartInterviewRequest,
    groq: GroqService = Depends(get_groq_service),
):
    """Start a new mock interview session."""
    try:
        prompt = MOCK_INTERVIEW_PROMPT.format(
            role=req.role,
            experience=req.experience,
            interview_type=req.interview_type,
            conversation_history="This is the start of the interview.",
        )
        reply = await groq.chat(INTERVIEW_COACH_SYSTEM, prompt)
        return {"success": True, "question": reply, "feedback": None}
    except GroqServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        print(f"❌ Interview start error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/answer")
async def submit_answer(
    req: AnswerRequest,
    groq: GroqService = Depends(get_groq_service),
):
    """Submit an answer and get feedback + next question."""
    try:
        prompt = MOCK_INTERVIEW_PROMPT.format(
            role=req.role,
            experience=0,
            interview_type="General",
            conversation_history=f"Q: {req.question}\nA: {req.answer}\n{req.conversation_history}",
        )
        reply = await groq.chat(INTERVIEW_COACH_SYSTEM, prompt)
        return {"success": True, "question": reply, "feedback": None}
    except GroqServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        print(f"❌ Interview answer error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/evaluate")
async def evaluate_answer(
    req: AnswerRequest,
    groq: GroqService = Depends(get_groq_service),
):
    """Evaluate a specific answer with detailed feedback."""
    try:
        prompt = ANSWER_EVALUATION_PROMPT.format(
            question=req.question,
            answer=req.answer,
            role=req.role,
        )
        result = await groq.chat_json(INTERVIEW_COACH_SYSTEM, prompt)
        return {"success": True, "data": result}
    except GroqServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/common-questions")
async def get_common_questions(
    req: CommonQuestionsRequest,
    groq: GroqService = Depends(get_groq_service),
):
    """Get common interview questions for a specific role."""
    try:
        prompt = (
            f"Generate {req.count} common {req.interview_type} interview questions "
            f"for the role of {req.role}. Return as a JSON array of strings."
        )
        result = await groq.chat_json(INTERVIEW_COACH_SYSTEM, prompt)
        return {"success": True, "data": result}
    except GroqServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
