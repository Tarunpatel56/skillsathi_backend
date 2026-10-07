import os
from dotenv import load_dotenv


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self):
        self.reload()

    def reload(self):
        # Let the project `.env` override any stale shell/IDE values.
        load_dotenv(override=True)

        self.APP_NAME = os.getenv("APP_NAME", "EduSarthi")
        self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"
        self.HOST = os.getenv("HOST", "0.0.0.0")
        self.PORT = int(os.getenv("PORT", "8000"))

        # Groq AI Configuration
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
        self.GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b").strip()
        self.GROQ_MAX_TOKENS = int(os.getenv("GROQ_MAX_TOKENS", "2048"))
        self.GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0.7"))


settings = Settings()
