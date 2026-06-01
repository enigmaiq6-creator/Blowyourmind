"""Generates English Spelling & Vocabulary trivia content using Gemini."""

from pathlib import Path
from typing import Optional

from tools.text_generation.gemini import GeminiTextGenerator
from tools.common.messenger import Messenger
from flows.trivia_spelling_orchestrator.schemas import TriviaVideoPlan


SPELLING_TRIVIA_SYSTEM_PROMPT = """
You are a professional English language expert and viral content creator.
Your task is to generate a trivia video plan with EXACTLY 3 multiple-choice questions
about English SPELLING, VOCABULARY MEANINGS (definitions), and WORD ORIGINS.

## STRICT RULES:
- ALL content MUST be in English. Never use any other language.
- Generate EXACTLY 3 questions, no more, no less.
- Each question must be UNIQUE and accurate. Never repeat questions across runs.
- Each question must have 3 options (A, B, C) with exactly ONE correct answer.
- Total video duration must exceed 60 seconds (~20-22 seconds per question).
- Questions should be engaging, educational, and genuinely challenging.
- Mix spelling tests, vocabulary definitions, and word origins across the 3 questions.
- Keep option text concise (under 8 words each) for mobile screen readability.
- Use fields: option_a, option_b, option_c (NOT an options dict).

## TIMING STRUCTURE (per question, 20 seconds total):
- [0s - 4s] Intro & Reading: Display question + options. TTS reads them.
- [4s - 14s] Countdown: 10-second timer with progress bar.
- [14s - 20s] Reveal: Correct answer highlighted. TTS announces answer.

## BACKGROUND VISUALS:
- Each question MUST have a UNIQUE background theme (no repeats).
- vertex_ai_prompt: Detailed prompt for Imagen AI (cinematic, educational, thematic).
- pexels_search_query: Short 2-4 word query for Pexels/Pixabay stock video search.

## OUTPUT JSON STRUCTURE:
{
  "video_metadata": {
    "topic": "English Spelling & Vocabulary",
    "total_duration_seconds": 60,
    "language": "en"
  },
  "questions": [
    {
      "id": 1,
      "question_text": "Which word is SPELLED CORRECTLY?",
      "option_a": "Accomodate",
      "option_b": "Accommodate",
      "option_c": "Acomodate",
      "correct_answer": "B",
      "visuals": {
        "vertex_ai_prompt": "A modern library with glowing books, cinematic lighting, 4k, hyperrealistic",
        "pexels_search_query": "library books education"
      },
      "tts_scripts": {
        "intro_and_options": "Which word is spelled correctly? Is it A, Accomodate, B, Accommodate, or C, Acomodate?",
        "reveal": "The correct answer is B, Accommodate!"
      },
      "timing": {
        "start": 0, "countdown_start": 4, "reveal_start": 14, "end": 20
      }
    }
  ]
}
"""


class SpellingTriviaGenerator:
    def __init__(self, text_gen: Optional[GeminiTextGenerator] = None):
        self.text_gen = text_gen or GeminiTextGenerator()

    def generate(self) -> TriviaVideoPlan:
        Messenger.info("Generating Spelling Trivia content via Gemini...")
        plan = self.text_gen.generate_text(
            prompt=SPELLING_TRIVIA_SYSTEM_PROMPT,
            schema=TriviaVideoPlan,
        )
        Messenger.success(f"Generated trivia: {plan.video_metadata.topic}")
        for q in plan.questions:
            Messenger.info(f"  Q{q.id}: {q.question_text} -> {q.correct_answer}")
        return plan

    def save_plan(self, plan: TriviaVideoPlan, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(plan.model_dump_json(indent=2), encoding="utf-8")
        Messenger.success(f"Trivia plan saved to: {output_path}")
