"""
Dependencies for API routes – shared services and utilities.
"""
from fastapi import HTTPException
from services.gemini_service import gemini_service, GeminiService
from services.groq_service import groq_service, GroqService


def get_groq_service() -> GroqService:
    """Dependency to inject the Groq service into route handlers."""
    try:
        groq_service.ensure_available()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return groq_service


def get_gemini_service() -> GeminiService:
    """Dependency to inject the Gemini service into route handlers."""
    try:
        gemini_service.ensure_available()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return gemini_service
