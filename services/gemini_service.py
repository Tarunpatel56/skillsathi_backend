"""
Gemini AI Service — Google Generative AI wrapper for EduSarthi.
Handles image analysis, lecture extraction, MCQ generation, and roadmaps.
"""
import json
import base64
from core.config import settings

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover - depends on local environment
    genai = None


class GeminiService:
    """Wrapper around Google Generative AI SDK."""

    def __init__(self):
        self._model = None

    def ensure_available(self) -> None:
        """Validate SDK and API key before handling a request."""
        if genai is None:
            raise RuntimeError(
                "Google Generative AI SDK is not installed. Run `pip install -r requirements.txt` in edusarthi_backend."
            )
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is missing in the backend environment.")

    @property
    def model(self):
        self.ensure_available()
        if self._model is None:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self._model = genai.GenerativeModel(settings.GEMINI_MODEL)
        return self._model

    async def analyze_image(self, image_base64: str, question: str = "") -> str:
        """Analyze an image (question/diagram) and provide a step-by-step solution."""
        system_prompt = (
            "You are an expert tutor. Analyze the image provided by the student. "
            "If it's a question, provide a step-by-step solution. "
            "If it's a diagram, explain its parts. "
            "Keep the tone encouraging and use simple language so a student can understand easily. "
            "Use emojis to make it engaging."
        )

        image_bytes = base64.b64decode(image_base64)
        image_part = {"mime_type": "image/jpeg", "data": image_bytes}

        prompt = system_prompt
        if question:
            prompt += f"\n\nStudent's question: {question}"
        else:
            prompt += "\n\nPlease analyze this image and explain it."

        try:
            response = self.model.generate_content([prompt, image_part])
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")

    async def extract_lecture_points(self, transcript: str) -> dict:
        """Extract key points, definitions, and practice questions from a lecture transcript."""
        prompt = (
            "I will provide you with a transcript of a classroom lecture. "
            "Your task is to:\n"
            "1. Extract the 5 most important key points\n"
            "2. Define all technical terms used\n"
            "3. Create 3 practice questions based on this lecture\n\n"
            "Return JSON with this exact format:\n"
            '{"key_points": ["point1", ...], "definitions": [{"term": "...", "definition": "..."}], '
            '"practice_questions": ["q1", "q2", "q3"]}\n'
            "Return ONLY valid JSON, no markdown.\n\n"
            f"Lecture transcript:\n{transcript}"
        )

        try:
            response = self.model.generate_content(prompt)
            return self._parse_json(response.text)
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")

    async def generate_mcqs(self, topic: str, count: int = 5) -> dict:
        """Generate MCQs on a given topic in JSON format."""
        prompt = (
            f"Generate {count} Multiple Choice Questions (MCQs) on the topic '{topic}'. "
            "For each question, provide 4 options and the correct answer. "
            "Return JSON with this exact format:\n"
            '{"questions": [{"question": "...", "options": ["A) ...", "B) ...", "C) ...", "D) ..."], '
            '"correct_answer": "A"}, ...]}\n'
            "Return ONLY valid JSON, no markdown."
        )

        try:
            response = self.model.generate_content(prompt)
            return self._parse_json(response.text)
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")

    async def generate_roadmap(self, goal: str) -> dict:
        """Generate a 30-day learning roadmap for a given career goal."""
        prompt = (
            f"The student wants to become a {goal}. "
            f"Based on the current date (March 2026), create a 30-day learning roadmap. "
            "Include topics to cover daily and a small project idea for each weekend. "
            "Return JSON with this format:\n"
            '{"goal": "...", "total_days": 30, '
            '"weeks": [{"week": 1, "theme": "...", "days": [{"day": 1, "topic": "...", "tasks": ["..."]}], '
            '"weekend_project": "..."}]}\n'
            "Return ONLY valid JSON, no markdown."
        )

        try:
            response = self.model.generate_content(prompt)
            return self._parse_json(response.text)
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")

    def _parse_json(self, raw: str) -> dict:
        """Parse JSON from Gemini response, handling markdown wrapping."""
        try:
            text = raw.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            return json.loads(text)
        except json.JSONDecodeError:
            return {"raw_response": raw}


# Singleton instance
gemini_service = GeminiService()
