"""
Phase 3 — Question Generation via Gemini Vision.

For each question page PNG:
  1. Loads the PNG
  2. Calls Gemini with subject label + page image
  3. Parses 10 MCQ questions from the JSON response
  4. Saves questions JSON to output/{subject}/generated/{book_id}_p{page_n}.json

Resumable: skips pages whose output JSON already exists.
"""
import json
import logging
import os
import time
import uuid
import warnings
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

SUBJECT_NAMES = {
    "quantitative_reasoning": "Quantitative Reasoning (Mathematics)",
    "logical_reasoning": "Logical Reasoning",
    "science_reasoning": "Science Reasoning",
    "reading_comprehension": "Reading Comprehension",
    "writing": "Writing",
}

_QUESTIONS_PER_PAGE = int(os.environ.get("QUESTIONS_PER_PAGE", "10"))

# Subjects that require a generated passage/scenario before questions
_PASSAGE_SUBJECTS = {"science_reasoning", "reading_comprehension"}

_PROMPT_TEMPLATE = """\
You are an expert Australian curriculum exam question writer for selective school entry.

You are looking at a page from an exam preparation book. \
The subject of this page is: {subject_name}.

Study the page carefully — understand the style, difficulty, and question structure shown.

{passage_instruction}

DIFFICULTY: 8 questions must be medium difficulty, 2 questions must be hard difficulty.

AUSTRALIAN CONTEXT — mandatory:
- Australian settings, names, cultural references throughout
- Currency in AUD ($), distances in kilometres, temperatures in Celsius
- Reference Australian places, flora, fauna, sports where natural
- Align to the Australian Curriculum for Year {year_level} students

QUESTION RULES:
- Every question stem must reference the passage above (e.g. "According to the passage...", \
"Based on Study 2...", "The author suggests...")
- Exactly 4 options: A, B, C, D — exactly one correct
- Wrong options must be plausible, not obviously silly
- One clear sentence explanation for the correct answer
- topic: a short Australian Curriculum strand label
- difficulty: exactly "medium" or "hard"
- confidence: 0.0–1.0 (your honest confidence the question and answer are correct)
- source_page_description: one sentence describing what you see on the PDF page

Return ONLY a valid JSON object — no markdown fences, no commentary:
{{
  "passage": "...(the full passage/scenario you invented, exactly as a student would read it)...",
  "questions": [
    {{
      "stem": "...",
      "option_a": "...",
      "option_b": "...",
      "option_c": "...",
      "option_d": "...",
      "correct_answer": "A|B|C|D",
      "explanation": "...",
      "topic": "...",
      "difficulty": "medium|hard",
      "confidence": 0.95,
      "source_page_description": "..."
    }}
  ]
}}
"""

_STANDALONE_PROMPT_TEMPLATE = """\
You are an expert Australian curriculum exam question writer for selective school entry.

You are looking at a page from an exam preparation book. \
The subject of this page is: {subject_name}.

Study the page carefully — understand the style, difficulty, and question structure shown.

Generate exactly {n} NEW multiple-choice questions inspired by what you see.
Do NOT copy or closely paraphrase any question visible on the page.

DIFFICULTY: 8 questions must be medium difficulty, 2 questions must be hard difficulty.

AUSTRALIAN CONTEXT — mandatory:
- Australian settings, names, cultural references throughout
- Currency in AUD ($), distances in kilometres, temperatures in Celsius
- Reference Australian places, flora, fauna, sports where natural
- Align to the Australian Curriculum for Year {year_level} students

QUESTION RULES:
- Exactly 4 options: A, B, C, D — exactly one correct
- Wrong options must be plausible, not obviously silly
- One clear sentence explanation for the correct answer
- topic: a short Australian Curriculum strand label
- difficulty: exactly "medium" or "hard"
- confidence: 0.0–1.0 (your honest confidence the question and answer are correct)
- source_page_description: one sentence describing what you see on the PDF page

Return ONLY a valid JSON object — no markdown fences, no commentary:
{{
  "passage": null,
  "questions": [
    {{
      "stem": "...",
      "option_a": "...",
      "option_b": "...",
      "option_c": "...",
      "option_d": "...",
      "correct_answer": "A|B|C|D",
      "explanation": "...",
      "topic": "...",
      "difficulty": "medium|hard",
      "confidence": 0.95,
      "source_page_description": "..."
    }}
  ]
}}
"""

_SCIENCE_PASSAGE_INSTRUCTION = """\
STEP 1 — INVENT A NEW SCENARIO:
Create a brand-new science experiment scenario in the same style as the page you see. \
It must include:
- A clear experimental context (what is being tested, by whom, where in Australia)
- 2 or 3 named Studies with specific data (measurements, tables described in plain text, \
e.g. "Study 1: Researchers measured X at three temperatures: 20°C (result: Y), \
30°C (result: Z), 40°C (result: W)")
- Enough data that a student can answer questions purely from reading the scenario

STEP 2 — GENERATE {n} QUESTIONS about your scenario."""

_READING_PASSAGE_INSTRUCTION = """\
STEP 1 — WRITE A NEW PASSAGE:
Write a brand-new reading passage (250–300 words) in the same style as the page you see. \
It must:
- Be set in an Australian context (Australian people, places, events, or environment)
- Have a clear topic, argument, or narrative arc
- Use vocabulary appropriate for Year {year_level} students
- Be self-contained — a student should be able to answer all questions from the passage alone

STEP 2 — GENERATE {n} QUESTIONS about your passage."""


def _get_gemini_model():
    key = os.environ.get("GEMINI_KEY", "")
    if not key:
        raise RuntimeError("GEMINI_KEY environment variable not set")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        import google.generativeai as genai
        genai.configure(api_key=key)
        model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
        return genai.GenerativeModel(model_name)


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1] if len(parts) > 1 else text
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    return text


def _call_gemini(model, image, prompt: str) -> dict:
    """Returns parsed JSON object with 'passage' and 'questions' keys."""
    response = model.generate_content([prompt, image])
    raw = _strip_fences(response.text)
    result = json.loads(raw)
    # Handle both old array format and new object format gracefully
    if isinstance(result, list):
        return {"passage": None, "questions": result}
    return result


def _build_question(raw: dict, subject: str, book_id: str, page_n: int,
                    passage: str | None) -> dict | None:
    stem = str(raw.get("stem", "")).strip()
    if not stem:
        return None

    difficulty = raw.get("difficulty", "medium")
    if difficulty not in ("medium", "hard"):
        difficulty = "medium"

    correct = str(raw.get("correct_answer", "")).strip().upper()
    if correct not in ("A", "B", "C", "D"):
        correct = "A"

    return {
        "id": str(uuid.uuid4()),
        "subject": subject,
        "stem": stem,
        "option_a": str(raw.get("option_a", "")).strip(),
        "option_b": str(raw.get("option_b", "")).strip(),
        "option_c": str(raw.get("option_c", "")).strip(),
        "option_d": str(raw.get("option_d", "")).strip(),
        "correct_answer": correct,
        "explanation": str(raw.get("explanation", "")).strip(),
        "topic": str(raw.get("topic", "")).strip(),
        "difficulty": difficulty,
        "confidence": float(raw.get("confidence", 0.85)),
        "source_book": book_id,
        "source_page": page_n,
        "source_page_description": str(raw.get("source_page_description", "")).strip(),
        "passage": passage,
        "review_status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def generate_page(
    page_n: int,
    image_path: str,
    subject: str,
    book_id: str,
    output_dir: str,
    briefing_data: dict,
    model=None,
) -> list:
    """
    Generate questions for one page PNG. Returns list of question dicts.
    Writes output JSON to output/{subject}/generated/{book_id}_p{page_n}.json.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        from PIL import Image
        img = Image.open(image_path)

    _model = model or _get_gemini_model()
    subject_name = SUBJECT_NAMES.get(subject, subject)
    year_level = briefing_data.get("target_year", "9-10")
    n = _QUESTIONS_PER_PAGE

    if subject in _PASSAGE_SUBJECTS:
        if subject == "science_reasoning":
            passage_instruction = _SCIENCE_PASSAGE_INSTRUCTION.format(n=n)
        else:
            passage_instruction = _READING_PASSAGE_INSTRUCTION.format(n=n, year_level=year_level)
        prompt = _PROMPT_TEMPLATE.format(
            subject_name=subject_name,
            n=n,
            year_level=year_level,
            passage_instruction=passage_instruction,
        )
    else:
        prompt = _STANDALONE_PROMPT_TEMPLATE.format(
            subject_name=subject_name,
            n=n,
            year_level=year_level,
        )

    result = _call_gemini(_model, img, prompt)
    passage = result.get("passage") or None
    raw_questions = result.get("questions", [])

    questions = []
    for raw in raw_questions:
        if not isinstance(raw, dict):
            continue
        q = _build_question(raw, subject, book_id, page_n, passage)
        if q:
            questions.append(q)

    out_dir = Path(output_dir) / subject / "generated"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{book_id}_p{page_n}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)

    logger.info(f"Page {page_n} ({subject}): {len(questions)} questions generated")
    return questions


def run(
    book_id: str,
    scratch_dir: str = None,
    output_dir: str = None,
    briefing_data: dict = None,
    briefing_path: str = None,
    test_pages: list = None,
) -> dict:
    """
    Phase 3: generate questions for all question pages.

    Args:
        test_pages: if given, only process these page numbers.

    Returns: {"generated": int, "skipped": int, "failed": int}
    """
    _scratch = scratch_dir or os.environ.get("SCRATCH_DIR", "/data/scratch")
    _output = output_dir or os.environ.get("OUTPUT_DIR", "/data/output")
    _delay = int(os.environ.get("API_DELAY_SECONDS", "2"))

    page_map_path = Path(_scratch) / book_id / "page_map.json"
    if not page_map_path.exists():
        raise FileNotFoundError(f"page_map.json not found at {page_map_path}. Run Phase 2 first.")

    with open(page_map_path, encoding="utf-8") as f:
        page_map = json.load(f)

    if briefing_data is None:
        import pipeline.briefing as briefing_module
        briefing_data = briefing_module.load(briefing_path)

    model = _get_gemini_model()
    stats = {"generated": 0, "skipped": 0, "failed": 0}

    for page_entry in page_map["pages"]:
        page_n = page_entry["page_number"]
        subject = page_entry["subject"]

        if test_pages and page_n not in test_pages:
            continue

        if subject == "skip":
            stats["skipped"] += 1
            continue

        out_path = Path(_output) / subject / "generated" / f"{book_id}_p{page_n}.json"
        if out_path.exists():
            logger.info(f"Page {page_n}: already generated — skipping")
            stats["skipped"] += 1
            continue

        # Find the PNG — matches any date suffix
        subject_dir = Path(_scratch) / book_id / "images" / subject
        matches = list(subject_dir.glob(f"{book_id}_*_p{page_n}.png"))
        if not matches:
            logger.warning(f"Page {page_n}: PNG not found in {subject_dir} — skipping")
            stats["failed"] += 1
            continue

        image_path = str(matches[0])

        try:
            questions = generate_page(
                page_n=page_n,
                image_path=image_path,
                subject=subject,
                book_id=book_id,
                output_dir=_output,
                briefing_data=briefing_data,
                model=model,
            )
            stats["generated"] += len(questions)
            time.sleep(_delay)
        except Exception as e:
            logger.error(f"Page {page_n}: generation failed: {e}")
            stats["failed"] += 1

    logger.info(f"Phase 3 complete for {book_id}: {stats}")
    return stats
