import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self):
        self.reload()

    def reload(self):
        # Look for .env in the backend folder first, then parent folders
        env_candidates = [
            BASE_DIR / ".env",
            BASE_DIR.parent / ".env",
            Path.cwd() / ".env",
        ]
        loaded = False
        for env_path in env_candidates:
            if env_path.is_file():
                load_dotenv(dotenv_path=env_path, override=True)
                loaded = True
                break
        if not loaded:
            load_dotenv(override=True)

        self.APP_NAME = os.getenv("APP_NAME", "EduSarthi")
        self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"
        self.HOST = os.getenv("HOST", "0.0.0.0")
        self.PORT = int(os.getenv("PORT", "8000"))

        # Groq AI Configuration
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
        self.GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
        self.GROQ_MAX_TOKENS = int(os.getenv("GROQ_MAX_TOKENS", "4096"))
        self.GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0.7"))


settings = Settings()
