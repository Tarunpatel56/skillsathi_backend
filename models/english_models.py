from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class ChatRequest(BaseModel):
    """General English chat with AI teacher."""
    message: str = Field(..., min_length=1, description="User's message to the English teacher")
    level: Optional[str] = Field("intermediate", description="User's English level: beginner / intermediate / advanced")
    language: Optional[str] = Field("both", description="Response language: english / hindi / both")


class GrammarCheckRequest(BaseModel):
    """Request to check grammar of a text."""
    text: str = Field(..., min_length=1, description="Text to check for grammar errors")


class VocabularyRequest(BaseModel):
    """Request to generate vocabulary words."""
    count: int = Field(5, ge=1, le=20, description="Number of words to generate")
    level: str = Field("intermediate", description="Difficulty level: beginner / intermediate / advanced")


class TranslationRequest(BaseModel):
    """Request to translate text."""
    text: str = Field(..., min_length=1, description="Text to translate")
    source_lang: str = Field("hindi", description="Source language")
    target_lang: str = Field("english", description="Target language")


class SentenceCheckRequest(BaseModel):
    """Request to check a user-written sentence."""
    sentence: str = Field(..., min_length=1, description="The sentence written by the user")
    topic: str = Field("general", description="Topic context for the sentence")
    level: str = Field("beginner", description="User's level")


class LessonTestRequest(BaseModel):
    """Request to generate a lesson test."""
    level: str = Field(..., description="User's level: beginner / intermediate / advanced")
    day: int = Field(..., ge=1, description="Day/lesson number")
    topic: str = Field(..., description="Lesson topic")
    count: int = Field(5, ge=3, le=10, description="Number of test questions")
    is_retry: bool = Field(False, description="If true, generate double the questions (retry after fail)")


class TestSubmitRequest(BaseModel):
    """Submit test answers for evaluation."""
    test_data: List[Dict] = Field(..., description="List of questions with user's answers")
    level: str = Field("beginner", description="User's level")
    day: int = Field(1, description="Day/lesson number")


class ChatResponse(BaseModel):
    """Standard AI response."""
    success: bool = True
    response: str
    message: Optional[str] = None


class GrammarCheckResponse(BaseModel):
    """Grammar check result."""
    success: bool = True
    original: str
    corrected: str
    errors: list = []
