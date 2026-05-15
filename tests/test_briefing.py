"""
Briefing parser tests — TEST-B-01 through TEST-B-15.
Run: pytest tests/test_briefing.py -v
"""
import os
import pytest
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"

# Import must happen after briefing.py exists — intentionally deferred per TDD
import pipeline.briefing as briefing


# ── TEST-B-01 ─────────────────────────────────────────────────────────────────
def test_b01_valid_briefing_parses_without_error():
    """[UNIT] valid briefing file parses without error."""
    result = briefing.load(str(FIXTURES / "sample_briefing.md"))
    assert isinstance(result, dict)


# ── TEST-B-02 ─────────────────────────────────────────────────────────────────
def test_b02_parsed_briefing_has_all_required_fields():
    """[CONTRACT] parsed briefing has all required fields."""
    result = briefing.load(str(FIXTURES / "sample_briefing.md"))
    required = [
        "file",
        "total_pages",
        "relevant_pages_start",
        "relevant_pages_end",
        "column_format",
        "has_figures",
        "figure_position",
        "subject_coverage",
        "target_year",
        "difficulty",
        "sample_pages",
        "answer_key_pages_start",
        "answer_key_pages_end",
        "known_issues",
    ]
    for field in required:
        assert field in result, f"Missing required field: {field}"


# ── TEST-B-03 ─────────────────────────────────────────────────────────────────
def test_b03_subject_coverage_is_list_of_dicts():
    """[CONTRACT] subject_coverage is a list of page-range dicts."""
    result = briefing.load(str(FIXTURES / "sample_briefing.md"))
    coverage = result["subject_coverage"]
    assert isinstance(coverage, list)
    assert len(coverage) >= 1

    valid_subjects = {
        "quantitative_reasoning", "logical_reasoning", "science_reasoning",
        "reading_comprehension", "writing", "skip",
    }
    for item in coverage:
        assert "pages_start" in item, f"Missing pages_start in: {item}"
        assert "pages_end" in item, f"Missing pages_end in: {item}"
        assert "subject" in item, f"Missing subject in: {item}"
        assert item["subject"] in valid_subjects, (
            f"Invalid subject '{item['subject']}' in coverage"
        )


# ── TEST-B-04 ─────────────────────────────────────────────────────────────────
def test_b04_column_format_is_valid():
    """[CONTRACT] column_format is one of the three valid values."""
    result = briefing.load(str(FIXTURES / "sample_briefing.md"))
    assert result["column_format"] in ("single_column", "double_column", "mixed")


# ── TEST-B-05 ─────────────────────────────────────────────────────────────────
def test_b05_get_subject_for_page_returns_correct_subject():
    """[UNIT] get_subject_for_page returns correct subject for known ranges."""
    data = briefing.load(str(FIXTURES / "sample_briefing.md"))
    # sample_briefing.md: pages 45–120 = logical_reasoning
    assert briefing.get_subject_for_page(data, 80) == "logical_reasoning"
    # pages 121–200 = quantitative_reasoning
    assert briefing.get_subject_for_page(data, 150) == "quantitative_reasoning"


# ── TEST-B-06 ─────────────────────────────────────────────────────────────────
def test_b06_get_subject_for_page_returns_skip():
    """[UNIT] get_subject_for_page returns 'skip' for skip ranges."""
    data = briefing.load(str(FIXTURES / "sample_briefing.md"))
    # pages 201–280 = skip
    assert briefing.get_subject_for_page(data, 240) == "skip"


# ── TEST-B-07 ─────────────────────────────────────────────────────────────────
def test_b07_get_subject_for_page_returns_none_outside_all_ranges():
    """[UNIT] get_subject_for_page returns None for pages outside all ranges."""
    data = briefing.load(str(FIXTURES / "sample_briefing.md"))
    result = briefing.get_subject_for_page(data, 999)
    assert result is None


# ── TEST-B-08 ─────────────────────────────────────────────────────────────────
def test_b08_is_relevant_page():
    """[UNIT] is_relevant_page correctly identifies in-range pages."""
    data = briefing.load(str(FIXTURES / "sample_briefing.md"))
    assert briefing.is_relevant_page(data, 100) is True
    assert briefing.is_relevant_page(data, 10) is False


# ── TEST-B-09 ─────────────────────────────────────────────────────────────────
def test_b09_is_answer_key_page():
    """[UNIT] is_answer_key_page correctly identifies answer key pages."""
    data = briefing.load(str(FIXTURES / "sample_briefing.md"))
    # answer_key_pages: 381–395
    assert briefing.is_answer_key_page(data, 385) is True
    assert briefing.is_answer_key_page(data, 100) is False


# ── TEST-B-10 ─────────────────────────────────────────────────────────────────
def test_b10_is_sample_page():
    """[UNIT] is_sample_page correctly identifies declared sample pages."""
    data = briefing.load(str(FIXTURES / "sample_briefing.md"))
    # sample_pages: 12, 67, 145
    assert briefing.is_sample_page(data, 67) is True
    assert briefing.is_sample_page(data, 68) is False


# ── TEST-B-11 ─────────────────────────────────────────────────────────────────
def test_b11_missing_file_raises_file_not_found():
    """[EDGE] missing briefing file raises FileNotFoundError with helpful message."""
    missing = "/tmp/does_not_exist_qbank.md"
    with pytest.raises(FileNotFoundError) as exc_info:
        briefing.load(missing)
    msg = str(exc_info.value)
    assert missing in msg
    assert "CLAUDE.md" in msg or "template" in msg.lower()


# ── TEST-B-12 ─────────────────────────────────────────────────────────────────
def test_b12_minimal_briefing_parses_with_defaults():
    """[EDGE] minimal briefing with only required fields parses correctly with sensible defaults."""
    result = briefing.load(str(FIXTURES / "sample_briefing_minimal.md"))
    assert isinstance(result, dict)
    assert result["sample_pages"] == []
    assert result["known_issues"] == []
    assert result["figure_position"] == "below_question"


# ── TEST-B-13 ─────────────────────────────────────────────────────────────────
def test_b13_invalid_subject_in_coverage_raises_value_error(tmp_path):
    """[EDGE] invalid subject in coverage raises ValueError with helpful message."""
    invalid_briefing = tmp_path / "invalid.md"
    invalid_briefing.write_text(
        "# PDF BRIEFING: Invalid\n\n"
        "## Basic Info\n"
        "- **file:** test.pdf\n"
        "- **total_pages:** 100\n"
        "- **relevant_pages:** 1–100\n\n"
        "## Layout\n"
        "- **column_format:** single_column\n\n"
        "## Subject Coverage\n"
        "- **pages 1–100:** mathematics\n\n"
        "## Year Level\n"
        "- **target_year:** 8\n"
        "- **difficulty:** medium\n"
    )
    with pytest.raises(ValueError) as exc_info:
        briefing.load(str(invalid_briefing))
    msg = str(exc_info.value)
    assert "mathematics" in msg
    assert any(s in msg for s in [
        "quantitative_reasoning", "logical_reasoning", "valid"
    ])


# ── TEST-B-14 ─────────────────────────────────────────────────────────────────
def test_b14_double_column_format_parsed():
    """[UNIT] double_column format is parsed correctly."""
    result = briefing.load(str(FIXTURES / "sample_briefing_double_col.md"))
    assert result["column_format"] == "double_column"


# ── TEST-B-15 ─────────────────────────────────────────────────────────────────
def test_b15_en_dash_page_range_parses_correctly(tmp_path):
    """[REGRESSION] en-dash (–) in page ranges does not crash the parser."""
    briefing_file = tmp_path / "endash.md"
    briefing_file.write_text(
        "# PDF BRIEFING: En-dash Test\n\n"
        "## Basic Info\n"
        "- **file:** test.pdf\n"
        "- **total_pages:** 120\n"
        "- **relevant_pages:** 46–120\n\n"  # en-dash U+2013
        "## Layout\n"
        "- **column_format:** single_column\n\n"
        "## Subject Coverage\n"
        "- **pages 46–120:** quantitative_reasoning\n\n"
        "## Year Level\n"
        "- **target_year:** 8\n"
        "- **difficulty:** medium\n"
    )
    result = briefing.load(str(briefing_file))
    assert result["relevant_pages_start"] == 46
    assert result["relevant_pages_end"] == 120
    coverage = result["subject_coverage"]
    assert coverage[0]["pages_start"] == 46
    assert coverage[0]["pages_end"] == 120
