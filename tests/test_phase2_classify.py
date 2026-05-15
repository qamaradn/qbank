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


@pytest.mark.slow
@pytest.mark.skipif(not GEMINI_AVAILABLE, reason="GEMINI_KEY not set")
@pytest.mark.parametrize("fname,expected_subject", [
    ("sample_qr_page.md",  "quantitative_reasoning"),
    ("sample_lr_page.md",  "logical_reasoning"),
    ("sample_sr_page.md",  "science_reasoning"),
    ("sample_rc_page.md",  "reading_comprehension"),
    ("sample_wr_page.md",  "writing"),
])
def test_p2_01_correct_subject_for_each_fixture(fname, expected_subject):
    """[CONTRACT] classifier returns correct subject for each of the 5 subjects."""
    data = briefing_module.load(str(FIXTURES / "sample_briefing.md"))
    content = (FIXTURES / fname).read_text()
    result = p2.classify_page(content, data, page_number=9999)
    assert result["subject"] == expected_subject, (
        f"{fname}: expected {expected_subject!r}, got {result['subject']!r}\n"
        f"Reasoning: {result['reasoning']}\n"
        f"Confidence: {result['confidence']}"
    )


@pytest.mark.slow
@pytest.mark.skipif(not GEMINI_AVAILABLE, reason="GEMINI_KEY not set")
def test_p2_04_answer_key_page_returns_answer_key():
    """[EDGE] answer key page returns 'answer_key'."""
    data = briefing_module.load(str(FIXTURES / "sample_briefing.md"))
    content = (FIXTURES / "sample_answer_key_page.md").read_text()
    result = p2.classify_page(content, data, page_number=9999)
    assert result["subject"] == "answer_key", (
        f"Expected 'answer_key', got {result['subject']!r}\nReasoning: {result['reasoning']}"
    )


@pytest.mark.slow
@pytest.mark.skipif(not GEMINI_AVAILABLE, reason="GEMINI_KEY not set")
def test_p2_05_theory_page_is_question_page_false():
    """[EDGE] theory/explanation page sets is_question_page=False."""
    data = briefing_module.load(str(FIXTURES / "sample_briefing.md"))
    content = (FIXTURES / "sample_theory_page.md").read_text()
    result = p2.classify_page(content, data, page_number=9999)
    assert result["is_question_page"] is False, (
        f"Expected is_question_page=False for theory page, got True\n"
        f"Subject: {result['subject']}, Reasoning: {result['reasoning']}"
    )
    valid_subjects = {
        "quantitative_reasoning", "logical_reasoning", "science_reasoning",
        "reading_comprehension", "writing",
    }
    assert result["subject"] in valid_subjects, (
        f"Theory page subject should be a real subject, got {result['subject']!r}"
    )


@pytest.mark.slow
@pytest.mark.skipif(not GEMINI_AVAILABLE, reason="GEMINI_KEY not set")
def test_p2_07_outside_briefing_range_uses_api():
    """[UNIT] page outside all briefing ranges: briefing_override=False, API used."""
    data = briefing_module.load(str(FIXTURES / "sample_briefing.md"))
    content = (FIXTURES / "sample_qr_page.md").read_text()
    result = p2.classify_page(content, data, page_number=9999)  # 9999 outside all ranges
    assert result["briefing_override"] is False, (
        "Expected API path (briefing_override=False) for page 9999"
    )


def test_p2_10_garbled_page_flags_low_confidence():
    """[EDGE] garbled OCR page → confidence < 0.5, needs_manual_review=True."""
    data = briefing_module.load(str(FIXTURES / "sample_briefing.md"))
    content = (FIXTURES / "sample_garbled_page.md").read_text()
    result = p2.classify_page(content, data, page_number=9999)
    assert result["confidence"] < 0.5, (
        f"Expected confidence < 0.5 for garbled page, got {result['confidence']:.2f}\n"
        f"Reasoning: {result['reasoning']}"
    )
    assert result["needs_manual_review"] is True


@pytest.mark.slow
def test_p2_08_page_map_json_written_correctly(tmp_path):
    """[INTEGRATION] run() writes page_map.json with correct structure."""
    import pipeline.phase1_normalise as p1

    # Run phase1 first to produce docling_output.json
    p1.run(
        book_id="act_5pages",
        pdf_path=str(FIXTURES / "act_5pages.pdf"),
        scratch_dir=str(tmp_path),
        briefing_path=str(FIXTURES / "sample_act_briefing.md"),
    )

    # Run phase2 — all pages use briefing override (no API needed)
    result = p2.run(
        book_id="act_5pages",
        scratch_dir=str(tmp_path),
        briefing_path=str(FIXTURES / "sample_act_briefing.md"),
    )

    page_map_path = tmp_path / "act_5pages" / "page_map.json"
    assert page_map_path.exists(), "page_map.json not written"

    assert result["book_id"] == "act_5pages"
    assert len(result["pages"]) > 0

    for page in result["pages"]:
        assert "page_number" in page, f"Missing page_number: {page}"
        assert "subject" in page
        assert "confidence" in page
        assert "is_question_page" in page
        assert isinstance(page["is_question_page"], bool)
        assert "needs_manual_review" in page
        assert "briefing_override" in page


@pytest.mark.slow
def test_p2_09_resumable_skips_pre_classified_pages(tmp_path):
    """[UNIT] run() skips pages already present in page_map.json."""
    import json
    import pipeline.phase1_normalise as p1

    # Run phase1 to produce docling_output.json
    p1.run(
        book_id="act_5pages",
        pdf_path=str(FIXTURES / "act_5pages.pdf"),
        scratch_dir=str(tmp_path),
        briefing_path=str(FIXTURES / "sample_act_briefing.md"),
    )

    # Pre-populate page_map with a sentinel entry for page 1
    pre_map = {
        "book_id": "act_5pages",
        "pages": [{
            "page_number": 1,
            "subject": "quantitative_reasoning",
            "confidence": 1.0,
            "is_question_page": True,
            "reasoning": "pre-classified-sentinel",
            "needs_manual_review": False,
            "briefing_override": True,
        }]
    }
    page_map_path = tmp_path / "act_5pages" / "page_map.json"
    page_map_path.write_text(json.dumps(pre_map))

    result = p2.run(
        book_id="act_5pages",
        scratch_dir=str(tmp_path),
        briefing_path=str(FIXTURES / "sample_act_briefing.md"),
    )

    # Page 1 must retain its sentinel reasoning — was NOT re-classified
    page1 = next(p for p in result["pages"] if p["page_number"] == 1)
    assert page1["reasoning"] == "pre-classified-sentinel", (
        f"Page 1 was re-classified (should be skipped). Got: {page1['reasoning']}"
    )
