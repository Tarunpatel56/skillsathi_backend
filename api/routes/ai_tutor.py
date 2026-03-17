"""
AI Tutor API Routes — Powered by Gemini AI
===========================================
Endpoints for image analysis, lecture notes, MCQ generation, and learning roadmaps.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from api.deps import get_gemini_service
from services.gemini_service import GeminiService

router = APIRouter(prefix="/ai-tutor", tags=["AI Tutor"])


# ── Request Models ───────────────────────────

class ImageAnalysisRequest(BaseModel):
    image_base64: str = Field(..., description="Base64-encoded image data")
    question: str = Field("", description="Optional question about the image")


class LectureNotesRequest(BaseModel):
    transcript: str = Field(..., description="Lecture transcript text")


class MCQRequest(BaseModel):
    topic: str = Field(..., description="Topic for MCQ generation")
    count: int = Field(5, ge=1, le=20, description="Number of MCQs to generate")


class RoadmapRequest(BaseModel):
    goal: str = Field(..., description="Career goal (e.g., Backend Developer)")


# ── Endpoints ────────────────────────────────

@router.post("/analyze-image")
async def analyze_image(
    req: ImageAnalysisRequest,
    gemini: GeminiService = Depends(get_gemini_service),
):
    """Analyze a student's image (question/diagram) and provide explanation."""
    try:
        result = await gemini.analyze_image(req.image_base64, req.question)
        return {"analysis": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lecture-notes")
async def extract_lecture_notes(
    req: LectureNotesRequest,
    gemini: GeminiService = Depends(get_gemini_service),
):
    """Extract key points, definitions, and practice questions from lecture transcript."""
    try:
        result = await gemini.extract_lecture_points(req.transcript)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-mcqs")
async def generate_mcqs(
    req: MCQRequest,
    gemini: GeminiService = Depends(get_gemini_service),
):
    """Generate MCQs on a given topic in JSON format."""
    try:
        result = await gemini.generate_mcqs(req.topic, req.count)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-roadmap")
async def generate_roadmap(
    req: RoadmapRequest,
    gemini: GeminiService = Depends(get_gemini_service),
):
    """Generate a 30-day learning roadmap for a career goal."""
    try:
        result = await gemini.generate_roadmap(req.goal)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
