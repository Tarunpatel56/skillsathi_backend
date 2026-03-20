"""
SkillSathi Backend – FastAPI Entry Point
========================================
AI-powered education platform for:
  • English Learning (Grammar, Vocabulary, Translation)
  • Interview Preparation (Mock Interviews, Answer Evaluation)
  • Aptitude & Quizzes (Math, Logic, Verbal, Data Interpretation)

Powered by Groq LLM (LLaMA 3.3)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from api.routes import english, interview, aptitude

# ── App Setup ─────────────────────────────────
app = FastAPI(
    title="SkillSathi API",
    description="AI-powered education platform – English, Interview Prep & Aptitude",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS (allow Flutter app & web clients) ───
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routes ──────────────────────────
app.include_router(english.router, prefix="/api/v1")
app.include_router(interview.router, prefix="/api/v1")
app.include_router(aptitude.router, prefix="/api/v1")


# ── Health Check ─────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    return {
        "app": settings.APP_NAME,
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "english": "/api/v1/english",
            "interview": "/api/v1/interview",
            "aptitude": "/api/v1/aptitude",
        },
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "groq_configured": bool(settings.GROQ_API_KEY)}


# ── Run with Uvicorn ─────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
