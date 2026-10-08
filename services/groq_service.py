"""
Groq API service - handles all LLM calls.
"""
import json

from groq import Groq

from core.config import settings


class GroqServiceError(Exception):
    """Raised when the Groq provider rejects a request or config is invalid."""

    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class GroqService:
    """Wrapper around the Groq SDK for chat completions."""

    def __init__(self):
        self.client = None
        self.api_key = ""
        self.model = ""
        self.max_tokens = 0
        self.temperature = 0.0
        self._refresh_client()

    def _refresh_client(self):
        """Reload `.env` values and rebuild the SDK client if config changed."""
        settings.reload()

        if not settings.GROQ_API_KEY:
            raise GroqServiceError(
                "Groq API key is missing. Set `GROQ_API_KEY` in the backend `.env` file.",
                status_code=500,
            )

        config_changed = (
            self.client is None
            or self.api_key != settings.GROQ_API_KEY
            or self.model != settings.GROQ_MODEL
            or self.max_tokens != settings.GROQ_MAX_TOKENS
            or self.temperature != settings.GROQ_TEMPERATURE
        )

        if config_changed:
            self.client = Groq(api_key=settings.GROQ_API_KEY)
            self.api_key = settings.GROQ_API_KEY
            self.model = settings.GROQ_MODEL
            self.max_tokens = settings.GROQ_MAX_TOKENS
            self.temperature = settings.GROQ_TEMPERATURE

    @staticmethod
    def _wrap_error(error: Exception) -> GroqServiceError:
        message = str(error)
        lowered = message.lower()

        if "organization_restricted" in lowered:
            return GroqServiceError(
                "The current Groq account is restricted. Please use a different Groq API key or contact Groq support for this account.",
                status_code=503,
            )

        if (
            "invalid api key" in lowered
            or "authentication" in lowered
            or "unauthorized" in lowered
        ):
            return GroqServiceError(
                "Groq API key is invalid or unauthorized. Update `GROQ_API_KEY` in the backend `.env` and retry.",
                status_code=401,
            )

        return GroqServiceError(f"Groq API error: {message}")

    async def chat(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Send a chat completion request and return the assistant's reply."""
        try:
            self._refresh_client()
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
        except Exception as error:
            if isinstance(error, GroqServiceError):
                raise
            raise self._wrap_error(error) from error

    async def chat_with_history(
        self,
        system_prompt: str,
        messages: list[dict],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Chat completion with full message history for multi-turn conversations."""
        try:
            self._refresh_client()
            all_messages = [{"role": "system", "content": system_prompt}] + messages
            response = self.client.chat.completions.create(
                model=self.model,
                messages=all_messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
            )
            return response.choices[0].message.content
        except Exception as error:
            if isinstance(error, GroqServiceError):
                raise
            raise self._wrap_error(error) from error

    async def chat_json(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float | None = None,
    ) -> dict:
        """Send a chat request and parse the response as JSON."""
        # Force JSON response via prompt engineering to ensure safety across models
        system_prompt += (
            "\n\nIMPORTANT: You must return ONLY valid JSON. "
            "Do not use LaTeX or backslashes in any string values. "
            "Write math expressions in plain text only (e.g. '7/9' not '\\frac{7}{9}'). "
            "Do not wrap the JSON in markdown code blocks."
        )
        raw = await self.chat(system_prompt, user_message, temperature)
        try:
            import re
            cleaned = raw.strip()

            # 1. Extract from markdown code block if present
            match = re.search(r'```(?:json)?\s*([\s\S]*?)```', cleaned)
            if match:
                cleaned = match.group(1).strip()
            else:
                # 2. Find the outermost JSON boundaries
                start_idx = cleaned.find('[')
                start_dict = cleaned.find('{')
                if start_idx != -1 and start_dict != -1:
                    start = min(start_idx, start_dict)
                else:
                    start = max(start_idx, start_dict)
                if start != -1:
                    end_idx = cleaned.rfind(']')
                    end_dict = cleaned.rfind('}')
                    end = max(end_idx, end_dict)
                    if end != -1 and end > start:
                        cleaned = cleaned[start:end + 1]

            # 3. Fix invalid JSON escape sequences produced by AI math content.
            #    JSON only allows: \" \\ \/ \b \f \n \r \t \uXXXX
            #    Any other \X is invalid and must be replaced with the literal char.
            def _fix_escapes(s: str) -> str:
                valid_escapes = set('"\\\/bfnrtu')
                result = []
                i = 0
                while i < len(s):
                    if s[i] == '\\' and i + 1 < len(s):
                        next_char = s[i + 1]
                        if next_char in valid_escapes:
                            # Valid escape – keep both characters
                            result.append(s[i])
                            result.append(next_char)
                            i += 2
                        else:
                            # Invalid escape – drop the backslash, keep the char
                            result.append(next_char)
                            i += 2
                    else:
                        result.append(s[i])
                        i += 1
                return ''.join(result)

            cleaned = _fix_escapes(cleaned)

            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            print(f"❌ JSON Decode Error: {e}\nRaw Response: {raw}")
            raise ValueError(f"AI returned invalid JSON: {e}. Raw: {raw[:200]}")


groq_service = GroqService()
