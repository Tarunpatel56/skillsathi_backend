from pydantic import BaseModel, Field
from typing import Optional, List


class StartInterviewRequest(BaseModel):
    """Start a new mock interview session."""
    role: str = Field(..., description="Job role, e.g. 'Software Engineer', 'Data Analyst'")
    experience: int = Field(0, ge=0, description="Years of experience")
    interview_type: str = Field("HR", description="Interview type: HR / Technical / Behavioral")


class AnswerRequest(BaseModel):
    """Submit an answer during a mock interview."""
    question: str = Field(..., description="The interview question that was asked")
    answer: str = Field(..., min_length=1, description="User's answer to the question")
    role: str = Field(..., description="Job role for context")
    conversation_history: Optional[str] = Field("", description="Previous Q&A for context")


class InterviewResponse(BaseModel):
    """Interview question or feedback response."""
    success: bool = True
    question: Optional[str] = None
    feedback: Optional[str] = None
    score: Optional[int] = None
    model_answer: Optional[str] = None


class CommonQuestionsRequest(BaseModel):
    """Request common interview questions for a role."""
    role: str = Field(..., description="Job role")
    count: int = Field(10, ge=1, le=30, description="Number of questions")
    interview_type: str = Field("HR", description="HR / Technical / Behavioral")
