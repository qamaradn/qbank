"""
Phase 2 classifier tests — P2-01 through P2-11.
Run all: pytest tests/test_phase2_classify.py -v
Run fast only: pytest tests/test_phase2_classify.py -v -m "not slow"
"""
import os
import pytest
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"
GEMINI_AVAILABLE = bool(os.environ.get("GEMINI_KEY"))

import pipeline.phase2_classify as p2
import pipeline.briefing as briefing_module


def test_p2_11_empty_markdown_raises_value_error():
    """[UNIT] classify_page() raises ValueError for empty markdown."""
    data = briefing_module.load(str(FIXTURES / "sample_briefing.md"))
    with pytest.raises(ValueError, match="empty"):
        p2.classify_page("", data, page_number=100)


def test_p2_06_briefing_override_skips_api():
    """[UNIT] classify_page() returns briefing subject when page is in coverage range."""
    data = briefing_module.load(str(FIXTURES / "sample_briefing.md"))
    # sample_briefing.md: pages 45–120 = logical_reasoning
    result = p2.classify_page("some content here", data, page_number=80)
    assert result["subject"] == "logical_reasoning"
    assert result["briefing_override"] is True
    assert result["confidence"] == 1.0
    assert "briefing" in result["reasoning"].lower()
    assert isinstance(result["is_question_page"], bool)
    assert isinstance(result["needs_manual_review"], bool)
