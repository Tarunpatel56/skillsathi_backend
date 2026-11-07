"""
Mass Spoken English Service
Provides structured curriculum data, interactive drills, and RAG knowledge-base integration
for the Mass Spoken English 50-chapter course.
Supports custom question counts and dynamic AI drill generation.
"""
import json
import os
import random
import re
from pathlib import Path
from typing import Dict, List, Optional, Any

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "mass_spoken_curriculum.json"

class MassSpokenService:
    def __init__(self):
        self._curriculum: Dict[str, Any] = {}
        self._chapters_by_id: Dict[int, Dict[str, Any]] = {}
        self._load_data()

    def _load_data(self):
        if not DATA_PATH.exists():
            return
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            self._curriculum = json.load(f)
            self._chapters_by_id.clear()
            for ch in self._curriculum.get("chapters", []):
                self._chapters_by_id[ch["id"]] = ch

    def get_all_chapters(self) -> List[Dict[str, Any]]:
        """Return list of all 50 chapters summary."""
        # Always make sure we have latest data
        if len(self._chapters_by_id) < 50:
            self._load_data()

        summaries = []
        for ch in self._curriculum.get("chapters", []):
            summaries.append({
                "id": ch["id"],
                "title": ch["title"],
                "hindi_title": ch["hindi_title"],
                "category": ch.get("category", "General"),
                "level": ch.get("level", "beginner"),
                "emoji": ch.get("emoji", "📖"),
                "page_start": ch.get("page_start", 1),
                "page_end": ch.get("page_end", 1),
                "structures_count": len(ch.get("structures", [])),
                "examples_count": len(ch.get("examples", [])),
                "drills_count": len(ch.get("sentence_builder_drills", [])),
                "quiz_count": len(ch.get("worksheet_quiz", [])),
            })
        return summaries

    def get_chapter(self, chapter_id: int) -> Optional[Dict[str, Any]]:
        """Return complete details of a specific chapter."""
        if len(self._chapters_by_id) < 50:
            self._load_data()
        return self._chapters_by_id.get(chapter_id)

    @staticmethod
    def _create_drill(hindi: str, english: str) -> dict:
        clean_en = re.sub(r'[?!.]+$', '', english).strip()
        words = clean_en.split()
        scrambled = words.copy()
        random.shuffle(scrambled)
        if scrambled == words and len(words) > 2:
            scrambled[0], scrambled[1] = scrambled[1], scrambled[0]
        return {
            "hindi": hindi,
            "english": english,
            "target_words": words,
            "scrambled_words": scrambled,
        }

    @staticmethod
    def _create_quiz(id_: int, hindi: str, english: str, formula: str = "") -> dict:
        clean_en = re.sub(r'[?!.]+$', '', english).strip()
        words = clean_en.split()
        distractors = [
            " ".join(reversed(words[:2])) + " " + " ".join(words[2:]) if len(words) > 2 else english + " not",
            english.replace("is", "was").replace("have", "had").replace("can", "should"),
            english.replace("don't", "didn't").replace("to", "for"),
        ]
        filtered = [d for d in distractors if d.lower() != english.lower()]
        opts = [english] + filtered[:3]
        random.shuffle(opts)
        return {
            "id": id_,
            "question": f"Translate into English: '{hindi}'",
            "hindi_sentence": hindi,
            "options": opts,
            "correct_answer": english,
            "explanation": f"सही अनुवाद है: '{english}'",
        }

    def get_practice_pack(self, chapter_id: int, count: int = 10) -> Optional[Dict[str, Any]]:
        """Return interactive drills, flashcards, and worksheet quiz for a chapter with custom count."""
        if len(self._chapters_by_id) < 50:
            self._load_data()

        ch = self._chapters_by_id.get(chapter_id)
        if not ch:
            return None

        examples = ch.get("examples", [])
        flashcards = []
        for ex in examples:
            flashcards.append({
                "front_hindi": ex["hindi"],
                "back_english": ex["english"],
                "hint": ch["title"]
            })

        # Start with pre-stored drills
        drills = list(ch.get("sentence_builder_drills", []))
        quiz = list(ch.get("worksheet_quiz", []))

        # Merge in all examples as drills and quizzes so we have a large pool of 15-20+ unique items
        existing_en = {d.get("english", "").strip().lower() for d in drills}
        for ex in examples:
            en = ex.get("english", "").strip()
            hi = ex.get("hindi", "").strip()
            if en and hi and en.lower() not in existing_en:
                existing_en.add(en.lower())
                drills.append(self._create_drill(hi, en))
                quiz.append(self._create_quiz(len(quiz) + 1, hi, en))

        # Always SHUFFLE so the starting 5-6 are NEVER identical on repeat visits
        combined = list(zip(drills, quiz))
        random.shuffle(combined)
        drills = [c[0] for c in combined]
        quiz = [c[1] for c in combined]

        # Re-number quiz cleanly
        for i, q in enumerate(quiz):
            q["id"] = i + 1

        if count > 0 and len(drills) > count:
            drills = drills[:count]
            quiz = quiz[:count]

        if count > 0 and len(flashcards) >= count:
            flashcards = flashcards[:count]

        return {
            "chapter_id": chapter_id,
            "chapter_title": ch["title"],
            "hindi_title": ch["hindi_title"],
            "emoji": ch.get("emoji", "📖"),
            "sentence_builder_drills": drills,
            "worksheet_quiz": quiz,
            "flashcards": flashcards,
            "golden_rules": ch.get("golden_rules", []),
            "structures": ch.get("structures", []),
            "requested_count": count,
            "total_available": len(drills)
        }

    def get_knowledge_context(self, chapter_id: int) -> str:
        """Condensed book knowledge string to inject into AI system prompt."""
        ch = self._chapters_by_id.get(chapter_id)
        if not ch:
            return ""

        structures_str = "\n".join([f"- {s['name']}: {s['formula']} ({s['hindi']})" for s in ch.get("structures", [])])
        rules_str = "\n".join([f"- {r}" for r in ch.get("golden_rules", [])])
        examples_str = "\n".join([f"- {ex['hindi']} => {ex['english']}" for ex in ch.get("examples", [])[:6]])

        return f"""
[MASS SPOKEN ENGLISH BOOK KNOWLEDGE - CHAPTER {ch['id']}: {ch['title']}]
Hindi Title: {ch['hindi_title']}
Definition: {ch['definition']}

Formulas & Structures:
{structures_str}

Golden Rules:
{rules_str}

Examples:
{examples_str}
"""

    async def generate_dynamic_drills(self, chapter_id: int, count: int, groq: Any) -> Dict[str, Any]:
        """Generate additional fresh practice sentences using Groq grounded in book rules."""
        ch = self._chapters_by_id.get(chapter_id)
        if not ch:
            return {"drills": [], "quiz": []}

        structures = ch.get("structures", [])
        formula_text = "; ".join([f"{s['name']}: {s['formula']}" for s in structures]) or ch["title"]

        prompt = f"""
Generate exactly {count} unique practical daily-life Hindi to English sentences for Mass Spoken English Chapter {chapter_id}: {ch['title']} ({ch.get('hindi_title', '')}).
Grammar Rule/Formula to practice: {formula_text}

Requirements:
- Everyday conversational Hindi sentences (office, college, market, friends, home).
- Accurate English translation following the chapter formula.

Output a JSON object with a 'questions' key:
{{"questions": [{{"hindi": "हिंदी वाक्य", "english": "English translation"}}]}}
"""
        try:
            res = await groq.chat_json(
                "You are an expert bilingual Spoken English teacher. Respond with a JSON object containing a 'questions' list.",
                prompt,
                max_tokens=2500,
                temperature=0.85,
                model="qwen/qwen3.8-27b",
            )
            items = []
            if isinstance(res, dict):
                items = res.get("questions", res.get("sentences", res.get("data", [])))
            elif isinstance(res, list):
                items = res

            new_drills = []
            new_quiz = []
            for i, it in enumerate(items):
                hindi = str(it.get("hindi", "")).strip()
                english = str(it.get("english", "")).strip()
                if not hindi or not english:
                    continue
                new_drills.append(self._create_drill(hindi, english))
                new_quiz.append(self._create_quiz(i + 1, hindi, english, formula_text))

            return {"drills": new_drills, "quiz": new_quiz}
        except Exception as e:
            print(f"Error in generate_dynamic_drills: {e}")
            return {"drills": [], "quiz": []}


_service_instance: Optional[MassSpokenService] = None

def get_mass_spoken_service() -> MassSpokenService:
    global _service_instance
    if _service_instance is None:
        _service_instance = MassSpokenService()
    return _service_instance
