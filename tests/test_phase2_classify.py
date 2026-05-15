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


@pytest.mark.slow
@pytest.mark.skipif(not GEMINI_AVAILABLE, reason="GEMINI_KEY not set")
def test_p2_02_result_has_required_fields_correct_types():
    """[CONTRACT] classify_page() result always has required fields with correct types."""
    data = briefing_module.load(str(FIXTURES / "sample_briefing.md"))
    content = (FIXTURES / "sample_qr_page.md").read_text()
    result = p2.classify_page(content, data, page_number=9999)  # outside range → API path
    assert isinstance(result["subject"], str)
    assert isinstance(result["confidence"], float)
    assert 0.0 <= result["confidence"] <= 1.0
    assert isinstance(result["is_question_page"], bool)
    assert isinstance(result["reasoning"], str) and result["reasoning"]
    assert isinstance(result["needs_manual_review"], bool)
    assert isinstance(result["briefing_override"], bool)
    assert result["briefing_override"] is False  # API path, not briefing


@pytest.mark.slow
@pytest.mark.skipif(not GEMINI_AVAILABLE, reason="GEMINI_KEY not set")
def test_p2_03_subject_always_valid():
    """[CONTRACT] subject is always one of 7 valid return values."""
    data = briefing_module.load(str(FIXTURES / "sample_briefing.md"))
    valid = {
        "quantitative_reasoning", "logical_reasoning", "science_reasoning",
        "reading_comprehension", "writing", "answer_key", "skip",
    }
    for fname in [
        "sample_qr_page.md", "sample_lr_page.md", "sample_sr_page.md",
        "sample_rc_page.md", "sample_wr_page.md",
    ]:
        content = (FIXTURES / fname).read_text()
        result = p2.classify_page(content, data, page_number=9999)
        assert result["subject"] in valid, (
            f"{fname}: invalid subject {result['subject']!r}\nReasoning: {result['reasoning']}"
        )
