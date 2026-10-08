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

    async def _chat_raw(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float | None = None,
        response_format: dict | None = None,
    ) -> str:
        """Low-level chat call. Optionally passes response_format to the Groq API."""
        try:
            self._refresh_client()
            kwargs = dict(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=temperature if temperature is not None else self.temperature,
                max_tokens=self.max_tokens,
            )
            if response_format:
                kwargs["response_format"] = response_format
            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content or ""
        except Exception as error:
            if isinstance(error, GroqServiceError):
                raise
            raise self._wrap_error(error) from error

    async def chat_json(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float | None = None,
        max_retries: int = 3,
    ) -> dict:
        """Send a chat request and return parsed JSON.

        Strategy:
        1. Try Groq native JSON mode (response_format=json_object) – guarantees
           valid JSON at the API level; no prompt tricks needed.
        2. If the model doesn't support JSON mode (raises an error), fall back to
           plain text with escape sanitisation + retry loop.
        """
        import re

        # ── Instruction that works for both JSON-mode and text-mode ──────────
        json_instruction = (
            "\n\nYou MUST respond with valid JSON only. "
            "No markdown. No prose. Just the raw JSON structure requested. "
            "CRITICAL: Do NOT use LaTeX or backslashes in string values. "
            "Write ALL math in plain text: use 'sqrt(16)' not '\\sqrt{16}', "
            "'pi' not '\\pi', '7/9' not '\\frac{7}{9}', "
            "'<=' not '\\leq', '>=' not '\\geq', 'x' not '\\times'."
        )
        full_system = system_prompt + json_instruction

        # ── Attempt 1: native JSON mode ───────────────────────────────────────
        try:
            raw = await self._chat_raw(
                full_system,
                user_message,
                temperature,
                response_format={"type": "json_object"},
            )
            if raw and raw.strip():
                return json.loads(raw)           # API already guarantees valid JSON
        except (GroqServiceError, Exception) as e:
            # JSON mode not supported by this model – fall through to text mode
            print(f"⚠️  JSON mode unavailable ({e}); falling back to text mode.")

        # ── Fallback: text mode with sanitisation + retries ───────────────────
        last_error: Exception = ValueError("No attempts made")

        for attempt in range(1, max_retries + 1):
            raw = await self._chat_raw(full_system, user_message, temperature)

            if not raw or not raw.strip():
                print(f"⚠️  Attempt {attempt}/{max_retries}: empty response. Retrying…")
                last_error = ValueError("AI returned an empty response.")
                continue

            try:
                cleaned = raw.strip()

                # Strip markdown fences
                match = re.search(r'```(?:json)?\s*([\s\S]*?)```', cleaned)
                if match:
                    cleaned = match.group(1).strip()
                else:
                    # Trim to outermost JSON boundary
                    s_arr, s_obj = cleaned.find('['), cleaned.find('{')
                    if s_arr != -1 and s_obj != -1:
                        start = min(s_arr, s_obj)
                    else:
                        start = max(s_arr, s_obj)
                    if start != -1:
                        e_arr, e_obj = cleaned.rfind(']'), cleaned.rfind('}')
                        end = max(e_arr, e_obj)
                        if end > start:
                            cleaned = cleaned[start:end + 1]

                if not cleaned:
                    raise ValueError("JSON body empty after trimming.")

                # ── Robust regex-based escape sanitiser ──────────────────────
                # JSON only allows: \" \\ \/ \b \f \n \r \t \uXXXX
                # Step 1: drop the backslash for any \X where X is NOT one of the
                #         valid single-char JSON escape characters.
                #         Handles: \sqrt → sqrt, \pi → pi, \div → div, \leq → leq …
                cleaned = re.sub(r'\\([^"\\/bfnrtu])', r'\1', cleaned)
                # Step 2: \u not followed by exactly 4 hex digits is also invalid.
                #         e.g. "unequal" written as \unequal → uunequal after this.
                cleaned = re.sub(r'\\u(?![0-9a-fA-F]{4})', 'u', cleaned)

                return json.loads(cleaned)

            except (json.JSONDecodeError, ValueError) as e:
                print(f"⚠️  Attempt {attempt}/{max_retries}: parse error – {e}\nRaw[:300]: {raw[:300]}")
                last_error = e

        raise ValueError(
            f"AI returned invalid JSON after {max_retries} attempts. Last error: {last_error}"
        )


groq_service = GroqService()
