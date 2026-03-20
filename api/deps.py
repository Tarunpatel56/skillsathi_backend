"""
Dependencies for API routes – shared services and utilities.
"""
from services.groq_service import groq_service, GroqService


def get_groq_service() -> GroqService:
    """Dependency to inject the Groq service into route handlers."""
    return groq_service
