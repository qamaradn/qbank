"""Phase 4: Generate questions from normalised page markdown and figure images."""

import json
import logging
import os
import re
import time
import uuid
import warnings
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

VALID_SUBJECTS = {
    "quantitative_reasoning", "logical_reasoning", "science_reasoning",
    "reading_comprehension", "writing",
}

_SUBJECT_NAMES = {
    "quantitative_reasoning": "Quantitative Reasoning",
    "logical_reasoning": "Logical Reasoning",
    "science_reasoning": "Science Reasoning",
    "reading_comprehension": "Reading Comprehension",
    "writing": "Writing",
}

_LATEX_RULE = """\
- Use LaTeX for ALL mathematical expressions: inline math between $...$ delimiters
  Examples: $x^2$, $\\sqrt{113}$, $\\frac{4}{3}\\pi r^3$, $\\sin\\theta$, $a_n$
  Do NOT use plain text like x^2, sqrt(x), or unicode like √
"""

_TEXT_PROMPT = """\
You are generating Australian selective school exam practice questions.
SUBJECT: {subject_name}
YEAR LEVEL: {year_level}
DIFFICULTY: {difficulty}

Study this page carefully — the style, difficulty, and question structure.
Generate exactly {n} NEW questions.

Rules:
- Answerable from knowledge alone, no figure needed
- Different numbers/names/contexts from originals
- Same difficulty as the examples shown
- Exactly 4 options (A B C D), exactly one correct
- Australian context ($AUD, km, Australian names where natural)
- One-sentence explanation for correct answer
- Do not copy or closely paraphrase any original question
{latex_rule}
Return ONLY a valid JSON array, no markdown, no preamble:
[{{"stem":"...","option_a":"...","option_b":"...","option_c":"...","option_d":"...","correct_answer":"A|B|C|D","explanation":"...","topic":"...","difficulty":"easy|medium|hard","confidence":0.0}}]

SOURCE PAGE:
{page_markdown}
"""

_WRITING_PROMPT = """\
You are generating Australian selective school writing prompts.
YEAR LEVEL: {year_level}
DIFFICULTY: {difficulty}

Study this page carefully — the style, difficulty, and prompt structure.
Generate exactly {n} NEW writing prompts.

Rules:
- Suitable for Year {year_level} students
- Australian context where natural
- One clear, engaging writing_prompt per item

Return ONLY a valid JSON array, no markdown, no preamble:
[{{"writing_prompt":"...","topic":"...","difficulty":"easy|medium|hard","confidence":0.0}}]

SOURCE PAGE:
{page_markdown}
"""

_FIGURE_PROMPT = """\
You are generating Australian selective school exam questions from a figure.
SUBJECT: {subject_name}
YEAR LEVEL: {year_level}

The attached image is a figure from an exam prep book.
Generate exactly {n} NEW questions using this SAME figure.

Rules:
- Every question answerable purely from the figure
- Do not require knowledge not visible in the figure
- Do not repeat what original questions already asked
- Exactly 4 options (A B C D), exactly one correct
- Each stem must reference the figure ("the diagram", "the graph", "the table", "the figure")
- One-sentence explanation for correct answer
{latex_rule}
ORIGINAL QUESTIONS THAT USED THIS FIGURE:
{original_questions}

Return ONLY a valid JSON array, no markdown, no preamble:
[{{"stem":"...","option_a":"...","option_b":"...","option_c":"...","option_d":"...","correct_answer":"A|B|C|D","explanation":"...","topic":"...","difficulty":"easy|medium|hard","confidence":0.0}}]
"""


_MATH_SUBJECTS = {"quantitative_reasoning", "science_reasoning", "logical_reasoning"}


def _build_text_prompt(markdown: str, subject: str, briefing_data: dict, n: int) -> str:
    year_level = briefing_data.get("target_year", "7-9")
    difficulty = briefing_data.get("difficulty", "medium")
    subject_name = _SUBJECT_NAMES.get(subject, subject)
    latex_rule = _LATEX_RULE if subject in _MATH_SUBJECTS else ""
    if subject == "writing":
        return _WRITING_PROMPT.format(
            year_level=year_level, difficulty=difficulty,
            n=n, page_markdown=markdown,
        )
    return _TEXT_PROMPT.format(
        subject_name=subject_name, year_level=year_level,
        difficulty=difficulty, n=n, page_markdown=markdown,
        latex_rule=latex_rule,
    )


def _build_figure_prompt(
    figure_path: str, original_qs: list, subject: str, briefing_data: dict, n: int
) -> str:
    year_level = briefing_data.get("target_year", "7-9")
    subject_name = _SUBJECT_NAMES.get(subject, subject)
    orig_text = "\n".join(f"- {q.get('stem', '')}" for q in original_qs[:5]) or "(none)"
    latex_rule = _LATEX_RULE if subject in _MATH_SUBJECTS else ""
    return _FIGURE_PROMPT.format(
        subject_name=subject_name, year_level=year_level,
        n=n, original_questions=orig_text, latex_rule=latex_rule,
    )


def _get_gemini_model(model_name: str = None):
    key = os.environ.get("GEMINI_KEY", "")
    if not key:
        raise RuntimeError("GEMINI_KEY not set — cannot generate without Gemini API key")
    if model_name is None:
        model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        import google.generativeai as genai
        genai.configure(api_key=key)
        return genai.GenerativeModel(model_name)


def normalise_math(text: str) -> str:
    """Wrap bare math expressions in $...$ if Gemini forgot LaTeX delimiters."""
    if not isinstance(text, str):
        return text
    # Already wrapped — leave alone (avoid double-wrapping)
    if "$" in text:
        return text
    # sqrt(x) → $\sqrt{x}$
    text = re.sub(r'\bsqrt\(([^)]+)\)', r'$\\sqrt{\1}$', text)
    # x^2 or x^{2} bare → $x^2$
    text = re.sub(r'(?<!\$)(\b[\w]+\^[\w{}]+)(?!\$)', r'$\1$', text)
    return text


def _normalise_fields(q: dict) -> dict:
    """Apply normalise_math to all text fields of a question."""
    text_fields = ("stem", "option_a", "option_b", "option_c", "option_d", "explanation")
    return {k: (normalise_math(v) if k in text_fields else v) for k, v in q.items()}


def _validate_question(q: dict, subject: str) -> dict:
    if subject == "writing":
        if not q.get("writing_prompt"):
            raise ValueError("Writing question missing writing_prompt")
        return {
            "writing_prompt": str(q["writing_prompt"]),
            "topic": str(q.get("topic", "")),
            "difficulty": str(q.get("difficulty", "medium")),
            "confidence": float(max(0.0, min(1.0, float(q.get("confidence", 0.0))))),
            "option_a": None,
            "option_b": None,
            "option_c": None,
            "option_d": None,
            "correct_answer": None,
        }
    correct = str(q.get("correct_answer", "")).upper().strip("(). ")
    if correct not in ("A", "B", "C", "D"):
        raise ValueError(f"Invalid correct_answer: {q.get('correct_answer')!r}")
    return {
        "stem": str(q.get("stem", "")),
        "option_a": str(q.get("option_a", "")),
        "option_b": str(q.get("option_b", "")),
        "option_c": str(q.get("option_c", "")),
        "option_d": str(q.get("option_d", "")),
        "correct_answer": correct,
        "explanation": str(q.get("explanation", "")),
        "topic": str(q.get("topic", "")),
        "difficulty": str(q.get("difficulty", "medium")),
        "confidence": float(max(0.0, min(1.0, float(q.get("confidence", 0.0))))),
        "writing_prompt": None,
    }


def parse_llm_response(
    text: str,
    expected_n: int,
    subject: str,
    book_id: str = "",
    page: int = 0,
) -> list:
    """Strip markdown fences, parse JSON array, validate questions."""
    stripped = text.strip()
    stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
    stripped = re.sub(r"\s*```$", "", stripped)
    stripped = stripped.strip()

    # Fix LaTeX backslashes Gemini sometimes emits without doubling.
    # Walk char by char: \\ → keep as \\, \" → keep as \", lone \ → double to \\
    # This handles both already-correct (\\frac) and bare (\frac) in one pass.
    buf = []
    i = 0
    while i < len(stripped):
        ch = stripped[i]
        if ch != "\\":
            buf.append(ch)
            i += 1
        elif i + 1 < len(stripped) and stripped[i + 1] in ("\\", '"'):
            buf.append("\\")
            buf.append(stripped[i + 1])
            i += 2
        else:
            buf.append("\\\\")
            i += 1
    stripped = "".join(buf)

    try:
        data = json.loads(stripped)
    except json.JSONDecodeError as e:
        logger.error(
            f"Invalid JSON from LLM (book={book_id!r}, page={page}): {e}\n"
            f"Raw (first 300 chars): {text[:300]}"
        )
        return []

    if not isinstance(data, list):
        logger.error(f"LLM returned non-list JSON (book={book_id!r}, page={page})")
        return []

    valid = []
    for item in data:
        try:
            validated = _validate_question(item, subject)
            valid.append(_normalise_fields(validated))
        except (ValueError, TypeError, KeyError) as e:
            logger.warning(f"Skipping malformed question (book={book_id!r}, page={page}): {e}")

    if len(valid) != expected_n:
        logger.warning(
            f"expected {expected_n}, got {len(valid)} "
            f"(book={book_id!r}, page={page})"
        )
    return valid


def generate_text_questions(
    markdown: str,
    subject: str,
    briefing_data: dict,
    n: int = 8,
    *,
    _gemini_model=None,
) -> list:
    """Generate n questions from page markdown via Gemini."""
    model = _gemini_model if _gemini_model is not None else _get_gemini_model()
    prompt = _build_text_prompt(markdown, subject, briefing_data, n)
    response = model.generate_content(prompt)
    questions = parse_llm_response(response.text, n, subject)
    return [{**q, "subject": subject, "review_status": "pending"} for q in questions]


def generate_figure_questions(
    figure_path: str,
    original_qs: list,
    subject: str,
    briefing_data: dict,
    n: int = 4,
    *,
    _gemini_model=None,
) -> list:
    """Generate n questions from a figure PNG via Gemini multimodal."""
    import PIL.Image  # noqa: PLC0415
    model = _gemini_model if _gemini_model is not None else _get_gemini_model()
    prompt = _build_figure_prompt(figure_path, original_qs, subject, briefing_data, n)
    image = PIL.Image.open(figure_path)
    response = model.generate_content([prompt, image])
    questions = parse_llm_response(response.text, n, subject)
    return [{**q, "subject": subject, "review_status": "pending"} for q in questions]


def run(
    book_id: str,
    output_dir: str = None,
    scratch_dir: str = None,
    briefing_path: str = None,
) -> dict:
    """
    Phase 4: generate questions for all classified question pages.
    Resumable: skips pages where output JSON already exists.
    """
    if scratch_dir is None:
        scratch_dir = os.getenv("SCRATCH_DIR", "/data/scratch")
    if output_dir is None:
        output_dir = os.getenv("OUTPUT_DIR", "/data/output")

    book_scratch = os.path.join(scratch_dir, book_id)
    page_map_path = os.path.join(book_scratch, "page_map.json")

    if not os.path.exists(page_map_path):
        raise FileNotFoundError(
            f"page_map.json not found at {page_map_path}\n"
            "Run Phase 2 first: phase2_classify.run(book_id, ...)"
        )

    with open(page_map_path, encoding="utf-8") as f:
        page_map = json.load(f)

    if briefing_path is None:
        pdf_dir = os.getenv("PDF_DIR", "/data/pdfs")
        briefing_path = os.path.join(pdf_dir, f"{book_id}.md")

    import pipeline.briefing as briefing_module  # noqa: PLC0415
    briefing_data = briefing_module.load(briefing_path)

    api_delay = int(os.getenv("API_DELAY_SECONDS", "2"))
    model = _get_gemini_model()
    n_qs = int(os.getenv("QUESTIONS_PER_PAGE", "8"))
    stats = {"generated": 0, "skipped": 0, "failed": 0}

    for page_entry in page_map["pages"]:
        page_n = page_entry["page_number"]
        subject = page_entry["subject"]

        if not page_entry.get("is_question_page", False) or subject in ("answer_key", "skip"):
            logger.info(f"Skipping {subject} page {page_n}")
            continue

        output_subdir = os.path.join(output_dir, subject, "generated")
        output_path = os.path.join(output_subdir, f"{book_id}_p{page_n}.json")

        if os.path.exists(output_path):
            logger.info(f"skipping already generated page {page_n}")
            stats["skipped"] += 1
            continue

        md_path = os.path.join(book_scratch, "pages", f"page_{page_n}.md")
        if not os.path.exists(md_path):
            logger.warning(f"Missing markdown for page {page_n}: {md_path}")
            stats["failed"] += 1
            continue

        with open(md_path, encoding="utf-8") as f:
            markdown = f.read()

        questions = generate_text_questions(
            markdown, subject, briefing_data, n=n_qs, _gemini_model=model
        )

        now = datetime.now(timezone.utc).isoformat()
        year_level = briefing_data.get("target_year", "7-9")
        enriched = [
            {
                "id": str(uuid.uuid4()),
                "source_book": book_id,
                "source_page": page_n,
                "year_level": year_level,
                "has_figure": False,
                "figure_path": None,
                "created_at": now,
                "reviewed_at": None,
                "edited": False,
                **q,
            }
            for q in questions
        ]

        os.makedirs(output_subdir, exist_ok=True)

        if not enriched:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(
                    {"generation_failed": True, "page_number": page_n,
                     "book_id": book_id, "questions": []},
                    f,
                )
            stats["failed"] += 1
        else:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(enriched, f, indent=2, ensure_ascii=False)
            stats["generated"] += len(enriched)

        time.sleep(api_delay)

    # ── Figure track ──────────────────────────────────────────────────────────
    # For each subject, scan output/{subject}/figures/*.json for figure items
    subjects_seen = {e["subject"] for e in page_map["pages"]
                     if e.get("is_question_page") and e["subject"] not in ("answer_key", "skip")}
    for subject in subjects_seen:
        figures_dir_path = os.path.join(output_dir, subject, "figures")
        if not os.path.isdir(figures_dir_path):
            continue
        for fig_json in sorted(Path(figures_dir_path).glob(f"{book_id}_*.json")):
            with open(fig_json, encoding="utf-8") as f:
                fig_item = json.load(f)

            if not fig_item.get("has_figure"):
                continue

            fig_png = fig_item.get("figure_path", "")
            if not fig_png or not os.path.exists(fig_png):
                logger.warning(f"Figure PNG missing: {fig_png}")
                continue

            output_path = str(fig_json).replace(".json", "_generated.json")
            if os.path.exists(output_path):
                logger.info(f"Skipping already generated figure: {fig_json.name}")
                stats["skipped"] += 1
                continue

            # content is raw page text; wrap as a minimal list for the prompt builder
            raw_content = fig_item.get("content", "")
            original_qs = [{"stem": raw_content}] if raw_content else []
            try:
                n_fig = int(os.getenv("FIGURE_QUESTIONS_PER_FIGURE", "4"))
                questions = generate_figure_questions(
                    fig_png, original_qs, subject, briefing_data,
                    n=n_fig, _gemini_model=model
                )
            except Exception as e:
                logger.error(f"Figure generation failed for {fig_json.name}: {e}")
                stats["failed"] += 1
                continue

            now = datetime.now(timezone.utc).isoformat()
            year_level = briefing_data.get("target_year", "7-9")
            enriched = [
                {
                    "id": str(uuid.uuid4()),
                    "source_book": book_id,
                    "source_page": fig_item.get("page_number"),
                    "year_level": year_level,
                    "has_figure": True,
                    "figure_path": fig_png,
                    "created_at": now,
                    "reviewed_at": None,
                    "edited": False,
                    **q,
                }
                for q in questions
            ]

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(enriched, f, indent=2, ensure_ascii=False)
            stats["generated"] += len(enriched)
            logger.info(f"Figure {fig_json.name}: {len(enriched)} questions generated")
            time.sleep(api_delay)

    logger.info(f"Phase 4 complete: {stats}")
    return stats
