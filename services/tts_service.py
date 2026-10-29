"""
Text-to-Speech (TTS) Service using Microsoft Edge Neural TTS.
Provides realistic, human-like adult female voices with natural Indian English cadence.
"""
import re
import base64
import logging
from typing import Optional, Dict
import edge_tts

logger = logging.getLogger("edusarthi.tts")

# Selected high-quality female voices
DEFAULT_FEMALE_VOICE = "en-IN-NeerjaExpressiveNeural"
FALLBACK_FEMALE_VOICE = "en-IN-NeerjaNeural"
US_FEMALE_VOICE = "en-US-JennyNeural"

AVAILABLE_VOICES: Dict[str, str] = {
    "neerja_expressive": "en-IN-NeerjaExpressiveNeural",  # Conversational Indian English Female (Default)
    "neerja_natural": "en-IN-NeerjaNeural",              # Clear Indian English Female
    "jenny_us": "en-US-JennyNeural",                     # Warm US English Female
}

# Regex to strip emojis and markdown formatting so speech remains human and smooth
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "\U0001F900-\U0001F9FF"  # supplemental symbols
    "\U0001FA70-\U0001FAFF"
    "]+",
    flags=re.UNICODE,
)


def clean_text_for_speech(text: str) -> str:
    """Clean text by stripping markdown, emojis, and unpronounceable characters."""
    if not text:
        return ""
    # Remove markdown bold/italics
    cleaned = re.sub(r"[*_~`#]", " ", text)
    # Remove bullet points and numbered lists at line starts
    cleaned = re.sub(r"^\s*[-*•\d+.]\s+", " ", cleaned, flags=re.MULTILINE)
    # Remove emojis
    cleaned = EMOJI_PATTERN.sub("", cleaned)
    # Collapse multiple spaces and newlines
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


class TTSService:
    def __init__(self):
        # Memory cache for frequent greetings and short phrases
        self._cache: Dict[str, bytes] = {}

    async def synthesize_mp3_bytes(
        self,
        text: str,
        voice: Optional[str] = None,
        rate: str = "-4%",
        pitch: str = "+1Hz",
    ) -> bytes:
        """
        Synthesize text into MP3 audio bytes using Microsoft Edge Neural TTS.
        """
        clean_text = clean_text_for_speech(text)
        if not clean_text:
            return b""

        selected_voice = voice or DEFAULT_FEMALE_VOICE
        cache_key = f"{selected_voice}_{rate}_{pitch}_{clean_text}"

        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            communicate = edge_tts.Communicate(
                text=clean_text,
                voice=selected_voice,
                rate=rate,
                pitch=pitch,
            )
            audio_bytes = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_bytes += chunk["data"]

            if audio_bytes:
                # Keep cache bounded
                if len(self._cache) > 200:
                    self._cache.pop(next(iter(self._cache)))
                self._cache[cache_key] = audio_bytes
                return audio_bytes

            raise RuntimeError("No audio received from primary neural voice")

        except Exception as e:
            logger.warning(
                "Primary TTS voice %s failed (%s). Falling back to %s",
                selected_voice,
                e,
                FALLBACK_FEMALE_VOICE,
            )
            # Fallback to secondary voice
            try:
                fallback_comm = edge_tts.Communicate(
                    text=clean_text,
                    voice=FALLBACK_FEMALE_VOICE,
                    rate=rate,
                    pitch=pitch,
                )
                fallback_bytes = b""
                async for chunk in fallback_comm.stream():
                    if chunk["type"] == "audio":
                        fallback_bytes += chunk["data"]
                return fallback_bytes
            except Exception as fe:
                logger.error("TTS synthesis completely failed: %s", fe)
                raise fe

    async def synthesize_base64(
        self,
        text: str,
        voice: Optional[str] = None,
        rate: str = "-4%",
        pitch: str = "+1Hz",
    ) -> str:
        """Synthesize text and return base64 encoded audio string."""
        audio_bytes = await self.synthesize_mp3_bytes(text, voice=voice, rate=rate, pitch=pitch)
        if not audio_bytes:
            return ""
        return base64.b64encode(audio_bytes).decode("utf-8")


_tts_service_instance: Optional[TTSService] = None


def get_tts_service() -> TTSService:
    global _tts_service_instance
    if _tts_service_instance is None:
        _tts_service_instance = TTSService()
    return _tts_service_instance

