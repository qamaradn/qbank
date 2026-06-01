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
    "verbal_reasoning": "Verbal Reasoning",
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

DIFFICULTY: Per passage — exactly 4 questions medium, 1 question hard (5 per passage, 10 total).

AUSTRALIAN CONTEXT — mandatory:
- Australian settings, names, cultural references throughout
- Currency in AUD ($), distances in kilometres, temperatures in Celsius
- Reference Australian places, flora, fauna, sports where natural
- Align to the Australian Curriculum for Year {year_level} students

QUESTION RULES:
- Each passage must have EXACTLY 5 questions — no more, no less
- Every question stem must reference its passage (e.g. "According to the passage...", \
"Based on Study 2...", "The author suggests...")
- Exactly 4 options: A, B, C, D — exactly one correct
- Wrong options must be plausible, not obviously silly
- One clear sentence explanation for the correct answer
- topic: a short Australian Curriculum strand label
- difficulty: exactly "medium" or "hard"
- confidence: 0.0–1.0 (your honest confidence the question and answer are correct)
- source_page_description: one sentence describing what you see on the PDF page
- NO LaTeX or math notation — write formulas in plain text (e.g. CaCO3, MgCl2, H2O, x^2)

Return ONLY a valid JSON object — no markdown fences, no commentary:
{{
  "passages": [
    {{
      "passage": "...(first full scenario/passage, exactly as a student would read it)...",
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
    }},
    {{
      "passage": "...(second full scenario/passage, different topic)...",
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
- NO LaTeX or math notation — write formulas in plain text (e.g. CaCO3, MgCl2, H2O, x^2)

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

_SAMPLE_PROMPT_TEMPLATE = """\
You are an expert exam question writer for selective school entry.

You are looking at a SAMPLE question from a {subject_name} exam.

Study it carefully — understand the reasoning skill it tests, the difficulty level, \
and the question style.

Generate exactly {n} NEW multiple-choice questions that test the SAME reasoning skills \
in the same style. Do NOT copy or closely paraphrase the sample question. \
Each question must be completely original but test similar {subject_name} skills.

DIFFICULTY: 8 questions must be medium difficulty, 2 questions must be hard difficulty.

AUSTRALIAN CONTEXT — welcome where natural, never forced:
- Australian names, places, flora, and fauna may appear where they fit organically
- Do NOT force Australian references into word relationships, codes, or analogies \
where they would feel artificial
- Align difficulty to Year {year_level} students

QUESTION RULES:
- Exactly 4 options: A, B, C, D — exactly one correct
- Wrong options must be plausible, not obviously silly
- One clear sentence explanation for the correct answer
- topic: short label for the reasoning skill tested (e.g. "Analogies", "Odd One Out", \
"Word Relationships", "Sequences", "Classifications", "Word Codes", "Hidden Words")
- difficulty: exactly "medium" or "hard"
- confidence: 0.0–1.0 (your honest confidence the question and answer are correct)
- source_page_description: one sentence describing the sample question you can see
- NO LaTeX notation — plain text only

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

_VR_SAMPLE_PROMPT_TEMPLATE = """\
You are an expert exam question writer for selective school entry.

You are looking at a SAMPLE question from a Verbal Reasoning exam.

Study it carefully — understand the reasoning skill it tests, the difficulty level, \
and the question style.

Generate exactly {n} NEW multiple-choice questions inspired by this sample. \
Do NOT copy or closely paraphrase it. Each question must be completely original.

QUESTION VARIETY — spread across these types (do not repeat the same type more than 3 times):
- Synonyms (which word is closest in meaning to X?)
- Antonyms (which word is most opposite to X?)
- Analogies (A is to B as C is to ?)
- Odd One Out (which word does NOT belong with the others?)
- Word Classifications (which word belongs to this group?)
- Complete the Sentence (choose the best word to fill the blank)
- Word Codes (if CAT = 312, what does DOG equal?)
- Hidden Words (find a word hidden across two words in a phrase)

DIFFICULTY: 8 questions must be medium difficulty, 2 questions must be hard difficulty.

CONTEXT — keep language natural and unforced:
- Australian names, places, or animals may appear where they fit naturally
- Do NOT force Australian references into word codes, analogies, or definitions \
where they would feel artificial
- Vocabulary must suit Year {year_level} students

QUESTION RULES:
- Exactly 4 options: A, B, C, D — exactly one correct
- Wrong options must be plausible, not obviously silly
- One clear sentence explanation for the correct answer
- topic: the exact VR type used (e.g. "Analogies", "Word Codes", "Hidden Words")
- difficulty: exactly "medium" or "hard"
- confidence: 0.0–1.0 (your honest confidence the question and answer are correct)
- source_page_description: one sentence describing the sample question you can see
- NO LaTeX notation — plain text only

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

_VR_SAMPLE_PROMPT_COMPACT = """\
You are an expert exam question writer for selective school entry.

You are looking at a SAMPLE question from a Verbal Reasoning exam.
Study it — understand the skill, style, and difficulty.

Generate exactly {n} NEW multiple-choice questions inspired by this sample. \
Do NOT copy it.

VARIETY: mix these types — Synonyms, Antonyms, Analogies, Odd One Out, \
Classifications, Complete the Sentence, Word Codes, Hidden Words.
Do not repeat the same type more than 3 times.

DIFFICULTY: 8 medium, 2 hard. Vocabulary suits Year {year_level} students.
Australian references welcome but never forced.

RULES: 4 options (A–D), one correct, explanation ONE sentence only, \
topic = the VR type used, difficulty = "medium" or "hard", \
confidence 0.0–1.0, source_page_description = one sentence.

Return ONLY valid JSON — no fences:
{{
  "passage": null,
  "questions": [
    {{
      "stem": "...",
      "option_a": "...", "option_b": "...", "option_c": "...", "option_d": "...",
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

_VR_SAMPLE_PROMPT_DIVERSE = """\
You are an expert verbal reasoning exam question writer for Australian selective school entry.

Use the SAMPLE question in this image ONLY to calibrate difficulty and year level — \
do NOT generate similar questions to it. Instead, generate {n} questions drawn freely \
from the full spectrum of verbal reasoning types below.

CORE TYPES (must include at least 1 each):
- Analogies: "Hot is to Cold as Day is to ?"
- Odd One Out: identify the word that does not belong
- Synonyms: find word closest in meaning
- Antonyms: find word most opposite in meaning
- Complete the Sentence: choose the best word for the blank
- Logical Deductions: "All X are Y. Z is X. Therefore..."

SECONDARY TYPES (include at least 2 across the 10 questions):
- Word Codes: if CAT=312, what does DOG equal?
- Hidden Words: find a word hidden across two adjacent words in a phrase
- Letter or Number Sequences: A, C, F, J, ?
- Double Meanings: one word fits two different definitions
- Making Words: take one letter from each given word to form a new word
- Compound Words: join two words to make one (e.g. FIRE + SIDE = FIRESIDE)

DIFFICULTY: 8 medium, 2 hard. Suit Year {year_level} students.
Australian places, animals, sports welcome where natural — never forced.

RULES: 4 options (A–D), one correct, explanation ONE sentence, \
topic = exact type name from above, difficulty = "medium" or "hard", \
confidence 0.0–1.0, source_page_description = one sentence about the sample.

Return ONLY valid JSON — no fences:
{{
  "passage": null,
  "questions": [
    {{
      "stem": "...",
      "option_a": "...", "option_b": "...", "option_c": "...", "option_d": "...",
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

# Registry of all VR prompt variants — select via VR_PROMPT env var
# compact  = trimmed, fast, low failure rate on flash-lite (default)
# full     = full variety list + explicit context rules
# diverse  = PNG as difficulty calibration only, draws from full VR taxonomy
# generic  = non-VR-specific, Australian context optional

_SCIENCE_PASSAGE_INSTRUCTION = """\
STEP 1 — INVENT TWO SEPARATE SCENARIOS:
Create two distinct science experiment scenarios in the same style as the page you see. \
Each must include:
- A different experimental context from the other (different topic, different Australian setting)
- 2 or 3 named Studies with specific data (measurements, tables described in plain text, \
e.g. "Study 1: Researchers measured X at three temperatures: 20°C (result: Y), \
30°C (result: Z), 40°C (result: W)")
- Enough data that a student can answer 5 questions purely from reading that scenario

STEP 2 — GENERATE 5 QUESTIONS per scenario (10 total)."""

_READING_PASSAGE_INSTRUCTION = """\
STEP 1 — WRITE TWO SEPARATE PASSAGES:
Write two distinct reading passages (150–180 words each) in the same style as the page you see. \
Each must:
- Have a different topic from the other
- Be set in an Australian context (Australian people, places, events, or environment)
- Have a clear topic, argument, or narrative arc
- Use vocabulary appropriate for Year {year_level} students
- Be self-contained — a student should be able to answer 5 questions from that passage alone

STEP 2 — GENERATE 5 QUESTIONS per passage (10 total)."""


def _get_gemini_model():
    key = os.environ.get("GEMINI_KEY", "")
    if not key:
        raise RuntimeError("GEMINI_KEY environment variable not set")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        import google.generativeai as genai
        genai.configure(api_key=key)
        # gemini-2.5-flash-lite: no thinking tokens, $0.10 input / $0.40 output
        # vs gemini-2.5-flash with thinking ON at $0.30 / $3.50 — ~10x cheaper
        # Vision capability (reading PNGs) is identical across both models.
        model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash-lite")
        generation_config = genai.GenerationConfig(
            response_mime_type="application/json",
        )
        return genai.GenerativeModel(model_name, generation_config=generation_config)


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1] if len(parts) > 1 else text
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    return text


def _sanitise_json(text: str) -> str:
    """Escape literal control characters inside JSON strings.

    Gemini occasionally embeds raw newlines/tabs in string values which makes
    json.loads fail with 'Invalid control character'. This walks the text and
    escapes any control character found inside a quoted string.
    """
    result = []
    in_string = False
    skip_next = False
    _CTRL = {'\n': '\\n', '\r': '\\r', '\t': '\\t'}
    for ch in text:
        if skip_next:
            result.append(ch)
            skip_next = False
        elif ch == '\\':
            result.append(ch)
            skip_next = True
        elif ch == '"':
            in_string = not in_string
            result.append(ch)
        elif in_string and ord(ch) < 32:
            result.append(_CTRL.get(ch, ' '))
        else:
            result.append(ch)
    return ''.join(result)


def _call_gemini(model, image, prompt: str, retries: int = 2) -> dict:
    """Returns parsed JSON object with 'passage' and 'questions' keys.

    Handles three formats from Gemini:
      - Multi-passage: {"passages": [{"passage": "...", "questions": [...]}]}
      - Single-passage: {"passage": "...", "questions": [...]}
      - Legacy array: [...]
    Multi-passage format tags each question with its own passage via '_passage'.
    Retries up to `retries` times on JSON parse failure.
    """
    last_err = None
    for attempt in range(1 + retries):
        if attempt > 0:
            logger.warning(f"Retrying Gemini call (attempt {attempt + 1}) after: {last_err}")
            time.sleep(2)
        response = model.generate_content([prompt, image])
        raw = _sanitise_json(_strip_fences(response.text))
        try:
            result = json.loads(raw)
        except json.JSONDecodeError as e:
            last_err = e
            continue
        break
    else:
        raise last_err

    # Multi-passage format (new default for SR and RC)
    if isinstance(result, dict) and "passages" in result:
        all_questions = []
        for block in result["passages"]:
            passage_text = block.get("passage") or None
            for q in block.get("questions", []):
                if isinstance(q, dict):
                    q["_passage"] = passage_text
                    all_questions.append(q)
        return {"passage": None, "questions": all_questions}

    # Legacy array format
    if isinstance(result, list):
        return {"passage": None, "questions": result}

    # Single-passage format (standalone subjects)
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
    top_passage = result.get("passage") or None
    raw_questions = result.get("questions", [])

    questions = []
    for raw in raw_questions:
        if not isinstance(raw, dict):
            continue
        # Multi-passage: each question carries its own _passage tag
        passage = raw.pop("_passage", None) or top_passage
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


def run_from_png_dir(
    book_id: str,
    png_dir: str,
    subject: str,
    output_dir: str = None,
    target_year: str = "9-10",
    difficulty: str = "medium",
) -> dict:
    """
    PNG-dir mode: each PNG is a single sample question.
    Gemini sees it and generates 10 similar standalone questions.
    Resumable: skips PNGs whose output JSON already exists.
    """
    _output = output_dir or os.environ.get("OUTPUT_DIR", "/data/output")
    _delay = int(os.environ.get("API_DELAY_SECONDS", "2"))

    pngs = sorted(Path(png_dir).glob("*.png"))
    if not pngs:
        raise FileNotFoundError(f"No PNG files found in {png_dir}")

    briefing_data = {"target_year": target_year, "difficulty": difficulty}
    subject_name = SUBJECT_NAMES.get(subject, subject)
    model = _get_gemini_model()
    stats = {"generated": 0, "skipped": 0, "failed": 0}

    for i, png_path in enumerate(pngs, start=1):
        out_path = Path(_output) / subject / "generated" / f"{book_id}_p{i:03d}.json"
        if out_path.exists():
            logger.info(f"PNG {i}/{len(pngs)} ({png_path.name}): already generated — skipping")
            stats["skipped"] += 1
            continue

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            from PIL import Image
            img = Image.open(png_path)

        if subject == "verbal_reasoning":
            vr_style = os.environ.get("VR_PROMPT", "compact")
            template = {
                "compact": _VR_SAMPLE_PROMPT_COMPACT,
                "full": _VR_SAMPLE_PROMPT_TEMPLATE,
                "diverse": _VR_SAMPLE_PROMPT_DIVERSE,
                "generic": _SAMPLE_PROMPT_TEMPLATE,
            }.get(vr_style, _VR_SAMPLE_PROMPT_COMPACT)
        else:
            template = _SAMPLE_PROMPT_TEMPLATE
        prompt = template.format(
            subject_name=subject_name,
            n=_QUESTIONS_PER_PAGE,
            year_level=target_year,
        )

        try:
            result = _call_gemini(model, img, prompt)
            raw_questions = result.get("questions", [])

            questions = []
            for raw in raw_questions:
                if not isinstance(raw, dict):
                    continue
                raw.pop("_passage", None)
                q = _build_question(raw, subject, book_id, i, passage=None)
                if q:
                    questions.append(q)

            out_path.parent.mkdir(parents=True, exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(questions, f, indent=2, ensure_ascii=False)

            logger.info(f"PNG {i}/{len(pngs)} ({png_path.name}): {len(questions)} questions")
            stats["generated"] += len(questions)
            time.sleep(_delay)
        except Exception as e:
            logger.error(f"PNG {i}/{len(pngs)} ({png_path.name}): failed: {e}")
            stats["failed"] += 1

    logger.info(f"PNG-dir phase 3 complete for {book_id}: {stats}")
    return stats
