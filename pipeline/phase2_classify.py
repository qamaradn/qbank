import os
import re
import json
import time
import logging
import warnings

import pipeline.briefing as briefing_module

logger = logging.getLogger(__name__)

VALID_SUBJECTS = {
    "quantitative_reasoning", "logical_reasoning", "science_reasoning",
    "reading_comprehension", "writing", "answer_key", "skip",
}

# Minimum fraction of printable ASCII characters required to attempt classification.
# Pages with fewer printable chars are considered garbled/unreadable.
_GARBLED_ASCII_THRESHOLD = float(os.environ.get("GARBLED_ASCII_THRESHOLD", "0.5"))


def _is_garbled(markdown: str) -> bool:
    """
    Return True when the page content is too corrupted to classify reliably.

    Strategy: count characters in the ASCII printable range (0x20–0x7E, plus
    common whitespace). If fewer than GARBLED_ASCII_THRESHOLD of all non-whitespace
    characters are printable ASCII, the page is considered garbled.
    """
    # Strip whitespace for the ratio check
    stripped = re.sub(r"\s+", "", markdown)
    if not stripped:
        return False  # Empty handled separately
    printable = sum(1 for c in stripped if 0x20 <= ord(c) <= 0x7E)
    ratio = printable / len(stripped)
    return ratio < _GARBLED_ASCII_THRESHOLD

_CLASSIFICATION_PROMPT = """\
You are classifying pages from Australian selective school exam prep books.

Classify this page into EXACTLY ONE of:
- quantitative_reasoning: maths, arithmetic, algebra, percentages, ratios,
  number patterns, sequences, word problems requiring calculation
- logical_reasoning: patterns, series, analogies, coding-decoding, puzzles,
  spatial reasoning, seating arrangements, deductive reasoning
- science_reasoning: biology, chemistry, physics, earth science,
  data interpretation, experiments, scientific method
- reading_comprehension: passages with questions, vocabulary, inference,
  main idea, author purpose, tone analysis
- writing: creative prompts, essay structure, grammar, punctuation,
  persuasive writing tasks
- answer_key: page is an answer grid or answer listing
- skip: cover, contents, index, ads, instructions, not relevant

Return ONLY valid JSON, no markdown fences, no explanation:
{{
  "subject": "<one of the values above>",
  "is_question_page": true,
  "confidence": 0.0,
  "reasoning": "<one sentence>"
}}

PAGE CONTENT:
{page_markdown}
"""


def classify_page(markdown: str, briefing_data: dict, page_number: int = None) -> dict:
    """
    Classify a page's subject using briefing override or Gemini Flash.

    Returns dict with keys:
        subject, confidence, is_question_page, reasoning,
        needs_manual_review, briefing_override
    """
    if not markdown or not markdown.strip():
        raise ValueError("Cannot classify empty page")

    # Garbled-content early exit: severely corrupted pages cannot be classified.
    if _is_garbled(markdown):
        return {
            "subject": "skip",
            "confidence": 0.1,
            "is_question_page": False,
            "reasoning": (
                "Page content is severely garbled (low printable-ASCII ratio). "
                "Manual review required."
            ),
            "needs_manual_review": True,
            "briefing_override": False,
        }

    # Briefing override: page in known coverage range → no API call
    if page_number is not None:
        subject = briefing_module.get_subject_for_page(briefing_data, page_number)
        if subject is not None:
            return {
                "subject": subject,
                "confidence": 1.0,
                "is_question_page": subject not in ("answer_key", "skip"),
                "reasoning": (
                    f"Briefing override: page {page_number} is in coverage range ({subject})"
                ),
                "needs_manual_review": False,
                "briefing_override": True,
            }

    # Gemini API path
    return _call_gemini(markdown, briefing_data)


def _call_gemini(markdown: str, briefing_data: dict) -> dict:
    key = os.environ.get("GEMINI_KEY", "")
    if not key:
        raise RuntimeError(
            "GEMINI_KEY not set — cannot classify without Gemini API key"
        )

    model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        import google.generativeai as genai
        genai.configure(api_key=key)
        model = genai.GenerativeModel(model_name)
        prompt = _CLASSIFICATION_PROMPT.format(page_markdown=markdown)
        response = model.generate_content(prompt)

    return _parse_gemini_response(response.text)


def _parse_gemini_response(text: str) -> dict:
    # Strip markdown fences if Gemini adds them
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Gemini returned invalid JSON: {e}\nRaw response: {text[:200]}")

    subject = data.get("subject", "")
    if subject not in VALID_SUBJECTS:
        raise ValueError(
            f"Gemini returned invalid subject: {subject!r}. "
            f"Valid: {sorted(VALID_SUBJECTS)}"
        )

    confidence = float(data.get("confidence", 0.0))
    confidence = max(0.0, min(1.0, confidence))

    return {
        "subject": subject,
        "confidence": confidence,
        "is_question_page": bool(data.get("is_question_page", True)),
        "reasoning": str(data.get("reasoning", "")),
        "needs_manual_review": confidence < 0.5,
        "briefing_override": False,
    }


def run(book_id: str, scratch_dir: str = None, briefing_path: str = None) -> dict:
    """Placeholder — implemented in Task 5."""
    raise NotImplementedError("run() not yet implemented")
