"""
Groq API service - handles all LLM calls.
"""
import json
import re

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

    # ── Low-level call ────────────────────────────────────────────────────────

    def _call_api(
        self,
        messages: list[dict],
        temperature: float,
        max_tokens: int,
        response_format: dict | None = None,
    ) -> str:
        """Synchronous Groq API call. Returns the model's text content."""
        self._refresh_client()
        kwargs = dict(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        if response_format:
            kwargs["response_format"] = response_format
        response = self.client.chat.completions.create(**kwargs)
        choice = response.choices[0]
        content = choice.message.content or ""
        if not content and hasattr(choice.message, "reasoning") and choice.message.reasoning:
            reasoning = choice.message.reasoning.strip()
            quotes = re.findall(r'"([^"\\]*(?:\\.[^"\\]*)*)"', reasoning)
            if quotes:
                content = quotes[-1]
            else:
                content = reasoning.split("\n")[-1]
        return content

    # ── JSON sanitiser ────────────────────────────────────────────────────────

    @staticmethod
    def _try_parse(text: str) -> dict | list | None:
        """Try to parse *text* as JSON. Return None if it fails."""
        try:
            return json.loads(text)
        except (json.JSONDecodeError, ValueError):
            return None

    @staticmethod
    def _sanitize_escapes(s: str) -> str:
        """
        Remove invalid JSON escape sequences so json.loads can succeed.

        JSON only allows: \\" \\\\ \\/ \\b \\f \\n \\r \\t \\uXXXX
        Anything else (e.g. \\\\sqrt, \\\\pi, \\\\div, \\\\leq) is fixed by
        dropping the backslash and keeping the character.
        Also fixes \\\\u not followed by exactly 4 hex digits.
        """
        # Step 1: drop backslash for any \X that is NOT a valid single-char escape.
        s = re.sub(r'\\([^"\\/bfnrtu])', r'\1', s)
        # Step 2: \u must be followed by exactly 4 hex digits – fix it otherwise.
        s = re.sub(r'\\u(?![0-9a-fA-F]{4})', 'u', s)
        return s

    @classmethod
    def _extract_json(cls, raw: str) -> dict | list:
        """
        Multi-strategy JSON extractor. Tries every reasonable way to get
        valid JSON out of a raw AI response string.

        Raises ValueError if all strategies fail.
        """
        if not raw or not raw.strip():
            raise ValueError("AI response is empty.")

        candidates: list[str] = []

        # Strategy 1: raw text as-is
        candidates.append(raw.strip())

        # Strategy 2: content inside a markdown code fence  ```json … ```
        fence_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', raw)
        if fence_match:
            candidates.append(fence_match.group(1).strip())

        # Strategy 3: trim to the outermost JSON boundary  [ … ] or { … }
        for start_ch, end_ch in [('[', ']'), ('{', '}')]:
            s = raw.find(start_ch)
            e = raw.rfind(end_ch)
            if s != -1 and e != -1 and e > s:
                candidates.append(raw[s:e + 1].strip())

        # Strategy 4 & 5: apply escape sanitisation to every candidate above
        sanitized = [cls._sanitize_escapes(c) for c in candidates]
        candidates.extend(sanitized)

        last_error: Exception = ValueError("No strategies succeeded.")
        for candidate in candidates:
            if not candidate:
                continue
            result = cls._try_parse(candidate)
            if result is not None:
                return result

        raise ValueError(
            f"All JSON extraction strategies failed. Last error: {last_error}. "
            f"Raw[:300]: {raw[:300]}"
        )

    # ── Public API ────────────────────────────────────────────────────────────

    async def chat(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Send a chat completion request and return the assistant's reply."""
        try:
            return self._call_api(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=temperature if temperature is not None else self.temperature,
                max_tokens=max_tokens or self.max_tokens,
            )
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
            all_messages = [{"role": "system", "content": system_prompt}] + messages
            return self._call_api(
                messages=all_messages,
                temperature=temperature if temperature is not None else self.temperature,
                max_tokens=max_tokens or self.max_tokens,
            )
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
    ) -> dict | list:
        """
        Send a chat request and return a parsed JSON object or array.

        Execution order:
        1. Try Groq native JSON mode  →  guarantees valid JSON at API level.
           Even if the parse somehow fails, run it through _extract_json().
        2. Fall back to plain-text mode with up to *max_retries* attempts,
           each using the multi-strategy _extract_json() sanitiser.

        This means the caller never sees a JSON parse error –
        either we return valid data or we raise after exhausting all retries.
        """
        # Instruction appended to the system prompt for both modes.
        json_note = (
            "\n\nRESPOND WITH VALID JSON ONLY — no markdown, no prose, no LaTeX. "
            "Write math in plain text: '7/9' not '\\frac{7}{9}', "
            "'sqrt(x)' not '\\sqrt{x}', 'pi' not '\\pi', "
            "'<=' not '\\leq', '>=' not '\\geq'."
        )
        full_system = system_prompt + json_note

        msgs = [
            {"role": "system", "content": full_system},
            {"role": "user", "content": user_message},
        ]
        temp = temperature if temperature is not None else self.temperature

        # ── Phase 1: native JSON mode ─────────────────────────────────────────
        try:
            raw = self._call_api(
                messages=msgs,
                temperature=temp,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"},
            )
            if raw and raw.strip():
                # JSON mode guarantees structure; _extract_json handles edge cases.
                return self._extract_json(raw)
            print("⚠️  JSON mode returned empty body; falling back to text mode.")
        except GroqServiceError:
            raise  # propagate auth / quota errors
        except Exception as e:
            # Model doesn't support JSON mode, or parse failed – try text mode.
            print(f"⚠️  JSON mode failed ({type(e).__name__}: {e}); using text mode.")

        # ── Phase 2: text mode with retries ──────────────────────────────────
        last_error: Exception = ValueError("No text-mode attempts made.")

        for attempt in range(1, max_retries + 1):
            try:
                raw = self._call_api(
                    messages=msgs,
                    temperature=temp,
                    max_tokens=self.max_tokens,
                )
                result = self._extract_json(raw)
                return result
            except GroqServiceError:
                raise
            except Exception as e:
                print(
                    f"⚠️  Text-mode attempt {attempt}/{max_retries} failed: {e}"
                )
                last_error = e

        raise ValueError(
            f"Quiz generation failed after {max_retries} attempts. "
            f"Last error: {last_error}"
        )


groq_service = GroqService()
