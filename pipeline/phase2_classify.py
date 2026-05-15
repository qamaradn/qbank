import os
import re
import json
import time
import logging

import pipeline.briefing as briefing_module

logger = logging.getLogger(__name__)

VALID_SUBJECTS = {
    "quantitative_reasoning", "logical_reasoning", "science_reasoning",
    "reading_comprehension", "writing", "answer_key", "skip",
}


def classify_page(markdown: str, briefing_data: dict, page_number: int = None) -> dict:
    """
    Classify a page's subject using briefing override or Gemini Flash.

    Returns dict with keys:
        subject, confidence, is_question_page, reasoning,
        needs_manual_review, briefing_override
    """
    if not markdown or not markdown.strip():
        raise ValueError("Cannot classify empty page")

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

    # Gemini path — not yet implemented (Task 2)
    raise NotImplementedError("Gemini API path not yet implemented — coming in Task 2")


def run(book_id: str, scratch_dir: str = None, briefing_path: str = None) -> dict:
    """Placeholder — implemented in Task 5."""
    raise NotImplementedError("run() not yet implemented")
