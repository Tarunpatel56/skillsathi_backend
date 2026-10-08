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
        max_retries: int = 3,
    ) -> dict:
        """Send a chat request and parse the response as JSON.

        Retries up to *max_retries* times on empty or unparseable responses.
        Also sanitises invalid JSON escape sequences that AI math content can produce.
        """
        import re

        # Append a concise JSON-only instruction without confusing the model.
        json_instruction = (
            "\n\nRESPOND WITH VALID JSON ONLY. "
            "No markdown fences. No explanatory text before or after the JSON. "
            "Do NOT use backslashes in string values (write fractions as '7/9', not '\\frac{7}{9}')."
        )
        full_system = system_prompt + json_instruction

        last_error: Exception = ValueError("No attempts made")

        for attempt in range(1, max_retries + 1):
            raw = await self.chat(full_system, user_message, temperature)

            # Guard: empty response from the model
            if not raw or not raw.strip():
                print(f"⚠️  Attempt {attempt}: AI returned empty response. Retrying…")
                last_error = ValueError("AI returned an empty response.")
                continue

            try:
                cleaned = raw.strip()

                # 1. Strip markdown code fences if present
                match = re.search(r'```(?:json)?\s*([\s\S]*?)```', cleaned)
                if match:
                    cleaned = match.group(1).strip()
                else:
                    # 2. Trim to the outermost JSON structure
                    start_arr = cleaned.find('[')
                    start_obj = cleaned.find('{')
                    if start_arr != -1 and start_obj != -1:
                        start = min(start_arr, start_obj)
                    else:
                        start = max(start_arr, start_obj)

                    if start != -1:
                        end_arr = cleaned.rfind(']')
                        end_obj = cleaned.rfind('}')
                        end = max(end_arr, end_obj)
                        if end != -1 and end > start:
                            cleaned = cleaned[start:end + 1]

                # Guard: still empty after trimming
                if not cleaned:
                    raise ValueError("JSON body is empty after cleaning.")

                # 3. Fix invalid JSON escape sequences.
                #    Valid JSON escapes: \" \\ \/ \b \f \n \r \t \uXXXX
                #    Everything else (e.g. \f from \frac, \t from \times) must be
                #    replaced by the bare character so json.loads succeeds.
                def _fix_escapes(s: str) -> str:
                    valid = set('"\\\/bfnrtu')
                    out, i = [], 0
                    while i < len(s):
                        if s[i] == '\\' and i + 1 < len(s):
                            nxt = s[i + 1]
                            if nxt in valid:
                                out.append(s[i])
                                out.append(nxt)
                            else:
                                # Drop the backslash; keep the next character.
                                out.append(nxt)
                            i += 2
                        else:
                            out.append(s[i])
                            i += 1
                    return ''.join(out)

                cleaned = _fix_escapes(cleaned)

                return json.loads(cleaned)

            except (json.JSONDecodeError, ValueError) as e:
                print(f"⚠️  Attempt {attempt}: JSON parse error – {e}\nRaw: {raw[:300]}")
                last_error = e
                # Retry on parse failure

        # All attempts exhausted
        raise ValueError(f"AI returned invalid JSON after {max_retries} attempts: {last_error}")


groq_service = GroqService()
