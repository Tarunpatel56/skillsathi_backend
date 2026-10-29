"""
Mass Spoken English Service
Provides structured curriculum data, interactive drills, and RAG knowledge-base integration
for the Mass Spoken English 150-page course.
"""
import json
import os
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
            for ch in self._curriculum.get("chapters", []):
                self._chapters_by_id[ch["id"]] = ch

    def get_all_chapters(self) -> List[Dict[str, Any]]:
        """Return list of all chapters summary (without heavy drill arrays)."""
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
        return self._chapters_by_id.get(chapter_id)

    def get_practice_pack(self, chapter_id: int) -> Optional[Dict[str, Any]]:
        """Return interactive drills, flashcards, and worksheet quiz for a chapter."""
        ch = self._chapters_by_id.get(chapter_id)
        if not ch:
            return None

        # Build flashcards from examples
        flashcards = []
        for ex in ch.get("examples", []):
            flashcards.append({
                "front_hindi": ex["hindi"],
                "back_english": ex["english"],
                "hint": ch["title"]
            })

        return {
            "chapter_id": chapter_id,
            "chapter_title": ch["title"],
            "hindi_title": ch["hindi_title"],
            "emoji": ch.get("emoji", "📖"),
            "sentence_builder_drills": ch.get("sentence_builder_drills", []),
            "worksheet_quiz": ch.get("worksheet_quiz", []),
            "flashcards": flashcards,
            "golden_rules": ch.get("golden_rules", []),
            "structures": ch.get("structures", [])
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

Golden Rules from Book:
{rules_str}

Book Examples:
{examples_str}
"""

_service_instance: Optional[MassSpokenService] = None

def get_mass_spoken_service() -> MassSpokenService:
    global _service_instance
    if _service_instance is None:
        _service_instance = MassSpokenService()
    return _service_instance

