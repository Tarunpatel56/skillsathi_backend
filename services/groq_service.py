"""
Groq API service – handles all LLM calls.
"""
import json
from core.config import settings

try:
    from groq import Groq
except ImportError:  # pragma: no cover - depends on local environment
    Groq = None


class GroqService:
    """Wrapper around the Groq SDK for chat completions."""

    def __init__(self):
        self._client = None
        self.model = settings.GROQ_MODEL
        self.max_tokens = settings.GROQ_MAX_TOKENS
        self.temperature = settings.GROQ_TEMPERATURE

    def ensure_available(self) -> None:
        """Validate SDK and API key before handling a request."""
        if Groq is None:
            raise RuntimeError(
                "Groq SDK is not installed. Run `pip install -r requirements.txt` in edusarthi_backend."
            )
        if not settings.GROQ_API_KEY:
            raise RuntimeError("GROQ_API_KEY is missing in the backend environment.")

    @property
    def client(self):
        self.ensure_available()
        if self._client is None:
            self._client = Groq(api_key=settings.GROQ_API_KEY)
        return self._client

    async def chat(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Send a chat completion request and return the assistant's reply."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Groq API error: {str(e)}")

    async def chat_with_history(
        self,
        system_prompt: str,
        messages: list[dict],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Chat completion with full message history for multi-turn conversations."""
        try:
            all_messages = [{"role": "system", "content": system_prompt}] + messages
            response = self.client.chat.completions.create(
                model=self.model,
                messages=all_messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Groq API error: {str(e)}")

    async def chat_json(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float | None = None,
    ) -> dict:
        """Send a chat request and parse the response as JSON."""
        raw = await self.chat(system_prompt, user_message, temperature)
        # Try to extract JSON from the response
        try:
            # Handle markdown-wrapped JSON (```json ... ```)
            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0].strip()
            elif "```" in raw:
                raw = raw.split("```")[1].split("```")[0].strip()
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"raw_response": raw}


# Singleton instance
groq_service = GroqService()
