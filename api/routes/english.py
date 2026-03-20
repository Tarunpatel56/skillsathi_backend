"""
English Learning Endpoints – Groq-powered English teacher.
Comprehensive curriculum based on book index with 49 lessons across 3 levels.
"""
from fastapi import APIRouter, Depends, HTTPException
from models.english_models import (
    ChatRequest, ChatResponse,
    GrammarCheckRequest, GrammarCheckResponse,
    VocabularyRequest, TranslationRequest,
    SentenceCheckRequest, LessonTestRequest, TestSubmitRequest,
)
from core.prompts import (
    ENGLISH_TEACHER_SYSTEM,
    GRAMMAR_CHECK_PROMPT,
    VOCABULARY_PROMPT,
    LESSON_GENERATION_PROMPT,
    SENTENCE_CHECK_PROMPT,
    LESSON_TEST_PROMPT,
)
from api.deps import get_groq_service
from services.groq_service import GroqService, GroqServiceError
import json

router = APIRouter(prefix="/english", tags=["English Learning"])


@router.post("/chat", response_model=ChatResponse)
async def english_chat(
    req: ChatRequest,
    groq: GroqService = Depends(get_groq_service),
):
    """Chat with the AI English teacher – bilingual support."""
    try:
        lang_instruction = ""
        if req.language == "both":
            lang_instruction = "\n\nIMPORTANT: Respond in BOTH English and Hindi. Give English answer first, then Hindi."
        elif req.language == "hindi":
            lang_instruction = "\n\nIMPORTANT: Respond primarily in Hindi with English terms where needed."
        else:
            lang_instruction = "\n\nIMPORTANT: Respond in English only."

        system = ENGLISH_TEACHER_SYSTEM + f"\n\nUser's level: {req.level}" + lang_instruction
        reply = await groq.chat(system, req.message)
        return ChatResponse(response=reply)
    except GroqServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/grammar-check")
async def grammar_check(
    req: GrammarCheckRequest,
    groq: GroqService = Depends(get_groq_service),
):
    """Check grammar and get corrections."""
    try:
        prompt = GRAMMAR_CHECK_PROMPT.format(text=req.text)
        result = await groq.chat_json(ENGLISH_TEACHER_SYSTEM, prompt)
        return {"success": True, "data": result}
    except GroqServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vocabulary")
async def generate_vocabulary(
    req: VocabularyRequest,
    groq: GroqService = Depends(get_groq_service),
):
    """Generate vocabulary words for the user's level."""
    try:
        prompt = VOCABULARY_PROMPT.format(count=req.count, level=req.level)
        result = await groq.chat_json(ENGLISH_TEACHER_SYSTEM, prompt)
        return {"success": True, "data": result}
    except GroqServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/translate", response_model=ChatResponse)
async def translate_text(
    req: TranslationRequest,
    groq: GroqService = Depends(get_groq_service),
):
    """Translate text between Hindi and English."""
    try:
        prompt = f"Translate the following from {req.source_lang} to {req.target_lang}:\n\n{req.text}"
        reply = await groq.chat(ENGLISH_TEACHER_SYSTEM, prompt, temperature=0.3)
        return ChatResponse(response=reply)
    except GroqServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check-sentence")
async def check_sentence(
    req: SentenceCheckRequest,
    groq: GroqService = Depends(get_groq_service),
):
    """Check a user-written sentence for correctness."""
    try:
        prompt = SENTENCE_CHECK_PROMPT.format(
            sentence=req.sentence,
            topic=req.topic,
            level=req.level,
        )
        result = await groq.chat_json(ENGLISH_TEACHER_SYSTEM, prompt)
        return {"success": True, "data": result}
    except GroqServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lesson-test/{level}/{day}")
async def generate_lesson_test(
    level: str,
    day: int,
    groq: GroqService = Depends(get_groq_service),
    count: int = 5,
    is_retry: bool = False,
):
    """Generate a test for a specific lesson."""
    if level not in ("beginner", "intermediate", "advanced"):
        raise HTTPException(status_code=400, detail="Level must be beginner, intermediate, or advanced")

    topics = get_level_topics(level)
    if day < 1 or day > len(topics):
        raise HTTPException(status_code=400, detail=f"Day must be between 1 and {len(topics)}")

    topic = topics[day - 1]["title"]
    actual_count = count * 2 if is_retry else count

    try:
        prompt = LESSON_TEST_PROMPT.format(
            day=day, level=level, topic=topic, count=actual_count
        )
        result = await groq.chat_json(ENGLISH_TEACHER_SYSTEM, prompt)
        return {"success": True, "data": result, "is_retry": is_retry}
    except GroqServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/evaluate-test")
async def evaluate_test(
    req: TestSubmitRequest,
    groq: GroqService = Depends(get_groq_service),
):
    """Evaluate submitted test answers."""
    try:
        prompt = f"""Evaluate the student's test answers. Level: {req.level}, Day: {req.day}

Test data:
{json.dumps(req.test_data, indent=2)}

Return a JSON with:
{{
  "total_questions": number,
  "correct": number correct,
  "wrong": number wrong,
  "score_percentage": percentage,
  "passed": true if score >= 60%,
  "answers": [
    {{
      "id": question id,
      "question": "short question text",
      "user_answer": "what user wrote",
      "correct_answer": "correct answer",
      "is_correct": true/false,
      "explanation": "why this is correct - English",
      "explanation_hindi": "Hindi mein explanation"
    }}
  ],
  "feedback": "Overall encouraging feedback in English",
  "feedback_hindi": "Hindi mein feedback",
  "retry_message": "If failed, encouraging message to try again with more practice"
}}
"""
        result = await groq.chat_json(ENGLISH_TEACHER_SYSTEM, prompt)
        return {"success": True, "evaluation": result}
    except GroqServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Level-specific topics from book index ────────
def get_level_topics(level: str) -> list:
    """Get topics for a specific level based on the book index."""
    if level == "beginner":
        return BEGINNER_TOPICS
    elif level == "intermediate":
        return INTERMEDIATE_TOPICS
    else:
        return ADVANCED_TOPICS


# Beginner: Basics (Book chapters 1-21)
BEGINNER_TOPICS = [
    {"id": 1, "title": "Self Introduction", "emoji": "👋", "subtitle": "Apna parichay dena sikho"},
    {"id": 2, "title": "Basic of English", "emoji": "📖", "subtitle": "English ki buniyaad"},
    {"id": 3, "title": "Greetings", "emoji": "🤝", "subtitle": "Namaste se Hello tak"},
    {"id": 4, "title": "Be Verb (is, am, are)", "emoji": "✨", "subtitle": "Hona/Rehna – I am, You are, He is"},
    {"id": 5, "title": "Imperative Sentences", "emoji": "📢", "subtitle": "Aadesh ya vinati ke vakya"},
    {"id": 6, "title": "Use of Has/Have, Had and Will", "emoji": "🔑", "subtitle": "Paas hona – mere paas hai"},
    {"id": 7, "title": "Demonstrative Pronoun", "emoji": "👉", "subtitle": "This, That, These, Those"},
    {"id": 8, "title": "Use of Want", "emoji": "🎯", "subtitle": "Chahna – I want, He wants"},
    {"id": 9, "title": "Use of Wanted", "emoji": "⏪", "subtitle": "Chahta tha – Past mein chahna"},
    {"id": 10, "title": "Use of Going to", "emoji": "🚶", "subtitle": "Jane wala hai – Future plans"},
    {"id": 11, "title": "Use of There", "emoji": "📍", "subtitle": "Wahan hai – There is/are"},
    {"id": 12, "title": "Use of Let", "emoji": "🤲", "subtitle": "Karne do – Let me, Let him"},
    {"id": 13, "title": "Use of Let's", "emoji": "🤝", "subtitle": "Chalo karte hain – Let's go"},
    {"id": 14, "title": "Use of Would like to", "emoji": "💭", "subtitle": "Pasand karunga – Polite requests"},
    {"id": 15, "title": "Use of Need to", "emoji": "⚡", "subtitle": "Zaroorat hai – I need to study"},
    {"id": 16, "title": "Use of Needed to", "emoji": "📋", "subtitle": "Zaroorat thi – Past needs"},
    {"id": 17, "title": "Use of Fond of", "emoji": "❤️", "subtitle": "Shaukeen hona – I am fond of"},
    {"id": 18, "title": "Use of About to", "emoji": "⏰", "subtitle": "Hone wala hai – About to happen"},
    {"id": 19, "title": "Use of Make/Gate", "emoji": "🔨", "subtitle": "Banana/Karwana – Make it happen"},
    {"id": 20, "title": "Use of All Modals", "emoji": "🎛️", "subtitle": "Can, Could, May, Might, Should"},
    {"id": 21, "title": "Use of All Tense", "emoji": "⏳", "subtitle": "Past, Present, Future – Sabhi kaal"},
]

# Intermediate: Advanced Grammar + Practice (Book chapters 22-43)
INTERMEDIATE_TOPICS = [
    {"id": 1, "title": "Use of Has to/Have to, Had to", "emoji": "💪", "subtitle": "Karna padta hai – Obligations"},
    {"id": 2, "title": "Use of Able to", "emoji": "🏋️", "subtitle": "Kar sakna – Ability expressions"},
    {"id": 3, "title": "Use of Want to", "emoji": "🎯", "subtitle": "Karna chahna – I want to learn"},
    {"id": 4, "title": "Use of Wanted to", "emoji": "⏪", "subtitle": "Karna chahta tha – Past desires"},
    {"id": 5, "title": "Use of All Prepositions", "emoji": "📐", "subtitle": "In, On, At, From, To – Sab sikho"},
    {"id": 6, "title": "Use of All W.H. Words", "emoji": "❓", "subtitle": "What, When, Where, Why, How"},
    {"id": 7, "title": "Use of All Passive Voice", "emoji": "🔄", "subtitle": "Karmvachya – Work was done"},
    {"id": 8, "title": "Verb List", "emoji": "📝", "subtitle": "Sabhi important verbs ki list"},
    {"id": 9, "title": "W.H. Words Vocabulary", "emoji": "📚", "subtitle": "Question words practice"},
    {"id": 10, "title": "Basic Spoken Words", "emoji": "🗣️", "subtitle": "Roz bolne wale English words"},
    {"id": 11, "title": "Daily Use Vocabulary", "emoji": "📅", "subtitle": "Har din ke useful words"},
    {"id": 12, "title": "Industry Vocabulary", "emoji": "🏭", "subtitle": "Office aur business ke words"},
    {"id": 13, "title": "Body & Diseases Vocabulary", "emoji": "🏥", "subtitle": "Sharir aur bimaari ke words"},
    {"id": 14, "title": "Vocabulary of Flowers & Fruits", "emoji": "🌺", "subtitle": "Phool aur phal ke naam"},
    {"id": 15, "title": "Bird's and Astrology Vocabulary", "emoji": "🐦", "subtitle": "Pakshi aur jyotish shabdavali"},
    {"id": 16, "title": "Maths Vocabulary", "emoji": "🔢", "subtitle": "Ganit ke English words"},
    {"id": 17, "title": "Foods Vocabulary", "emoji": "🍕", "subtitle": "Khane peene ke English naam"},
    {"id": 18, "title": "Relation Worms & Insects Vocabulary", "emoji": "🐛", "subtitle": "Rishte, keede makode ke naam"},
    {"id": 19, "title": "Stationery Vocabulary", "emoji": "✏️", "subtitle": "Stationery items English mein"},
    {"id": 20, "title": "Factory and Sports Vocabulary", "emoji": "⚽", "subtitle": "Factory aur khel ke words"},
    {"id": 21, "title": "Sound, Music & Weather Vocabulary", "emoji": "🎵", "subtitle": "Aawaz, sangeet aur mausam"},
    {"id": 22, "title": "Colours and Judiciary Vocabulary", "emoji": "🎨", "subtitle": "Rang aur kanoon ke words"},
]

# Advanced: Professional + Practice Worksheets (Book chapters 44-49 + worksheets)
ADVANCED_TOPICS = [
    {"id": 1, "title": "Professions & Occupations Vocabulary", "emoji": "👔", "subtitle": "Peshon ke English naam"},
    {"id": 2, "title": "Buildings and Months Vocabulary", "emoji": "🏢", "subtitle": "Imaaraton aur mahinon ke naam"},
    {"id": 3, "title": "Important Vocabulary", "emoji": "⭐", "subtitle": "Zaroori English shabdavali"},
    {"id": 4, "title": "Miscellaneous Words Vocabulary", "emoji": "📦", "subtitle": "Aur bohot saare useful words"},
    {"id": 5, "title": "Everyday Daily Vocabulary", "emoji": "🌅", "subtitle": "Roz ke English expressions"},
    {"id": 6, "title": "Conversation Sheets", "emoji": "💬", "subtitle": "English mein baat-cheet practice"},
    {"id": 7, "title": "Worksheet Practice 1 - Basics Review", "emoji": "📝", "subtitle": "Basic English revision practice"},
    {"id": 8, "title": "Worksheet Practice 2 - Tense Review", "emoji": "📝", "subtitle": "Tenses ka complete revision"},
    {"id": 9, "title": "Worksheet Practice 3 - Verbs Review", "emoji": "📝", "subtitle": "Verbs ka mashq"},
    {"id": 10, "title": "Worksheet Practice 4 - Sentences", "emoji": "📝", "subtitle": "Vakyataon ka abhyas"},
    {"id": 11, "title": "Worksheet Practice 5 - Translation", "emoji": "📝", "subtitle": "Hindi se English translation"},
    {"id": 12, "title": "Worksheet Practice 6 - Grammar", "emoji": "📝", "subtitle": "Grammar ka complete revision"},
    {"id": 13, "title": "Worksheet Practice 7 - Vocabulary", "emoji": "📝", "subtitle": "Shabdavali ka test"},
    {"id": 14, "title": "Worksheet Practice 8 - Modals", "emoji": "📝", "subtitle": "Can, Could, May practice"},
    {"id": 15, "title": "Worksheet Practice 9 - Prepositions", "emoji": "📝", "subtitle": "Prepositions ka mashq"},
    {"id": 16, "title": "Worksheet Practice 10 - Passive Voice", "emoji": "📝", "subtitle": "Passive voice practice"},
    {"id": 17, "title": "Worksheet Practice 11-14", "emoji": "📝", "subtitle": "Mixed practice worksheets"},
    {"id": 18, "title": "Worksheet Practice 15-17", "emoji": "📝", "subtitle": "Advanced mixed practice"},
    {"id": 19, "title": "Worksheet Practice 18-19", "emoji": "📝", "subtitle": "Final practice worksheets"},
    {"id": 20, "title": "Worksheet Practice 20 - Final Test", "emoji": "🏆", "subtitle": "Final comprehensive test"},
]


@router.get("/levels")
async def get_levels():
    """Get all available levels with their topics."""
    return {
        "success": True,
        "levels": {
            "beginner": {
                "name": "Beginner",
                "emoji": "🌱",
                "description": "English ki buniyaad – Basics se shuru karo",
                "total_lessons": len(BEGINNER_TOPICS),
                "topics": BEGINNER_TOPICS,
            },
            "intermediate": {
                "name": "Intermediate",
                "emoji": "📚",
                "description": "Advanced grammar aur vocabulary sikho",
                "total_lessons": len(INTERMEDIATE_TOPICS),
                "topics": INTERMEDIATE_TOPICS,
            },
            "advanced": {
                "name": "Advanced",
                "emoji": "🎓",
                "description": "Professional English aur practice worksheets",
                "total_lessons": len(ADVANCED_TOPICS),
                "topics": ADVANCED_TOPICS,
            },
        },
    }


@router.post("/lesson/{level}/{day}")
async def generate_lesson(
    level: str,
    day: int,
    groq: GroqService = Depends(get_groq_service),
):
    """Generate an AI-powered day-wise English lesson."""
    if level not in ("beginner", "intermediate", "advanced"):
        raise HTTPException(status_code=400, detail="Level must be beginner, intermediate, or advanced")

    topics = get_level_topics(level)
    if day < 1 or day > len(topics):
        raise HTTPException(status_code=400, detail=f"Day must be between 1 and {len(topics)}")

    topic_info = topics[day - 1]
    topic = topic_info["title"]
    try:
        prompt = LESSON_GENERATION_PROMPT.format(day=day, level=level, topic=topic)
        result = await groq.chat_json(ENGLISH_TEACHER_SYSTEM, prompt)

        # Add metadata
        if isinstance(result, dict):
            result["day"] = day
            result["level"] = level
            result["topic_emoji"] = topic_info.get("emoji", "📖")
            result["topic_subtitle"] = topic_info.get("subtitle", "")
            result["has_next"] = day < len(topics)
            result["total_lessons"] = len(topics)

        return result
    except GroqServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
