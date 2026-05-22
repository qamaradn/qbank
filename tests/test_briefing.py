"""Briefing parser tests."""
import pytest
from pathlib import Path
from pipeline.briefing import load, get_subject_for_page, is_relevant_page

FIXTURE = Path(__file__).parent / "fixtures" / "sample_briefing.md"


@pytest.fixture
def briefing(tmp_path):
    content = """# PDF BRIEFING: Test Book

## Basic Info
- **file:** test_book.pdf
- **relevant_pages:** 10–50
- **target_year:** 9-10
- **difficulty:** medium

## Subject Coverage
- **pages 10–20:** quantitative_reasoning
- **pages 21–35:** science_reasoning
- **pages 36–50:** reading_comprehension
"""
    p = tmp_path / "test.md"
    p.write_text(content)
    return str(p)


def test_load_basic_fields(briefing):
    d = load(briefing)
    assert d["file"] == "test_book.pdf"
    assert d["relevant_pages_start"] == 10
    assert d["relevant_pages_end"] == 50
    assert d["target_year"] == "9-10"
    assert d["difficulty"] == "medium"


def test_load_subject_coverage(briefing):
    d = load(briefing)
    assert len(d["subject_coverage"]) == 3
    subjects = [e["subject"] for e in d["subject_coverage"]]
    assert "quantitative_reasoning" in subjects
    assert "science_reasoning" in subjects
    assert "reading_comprehension" in subjects


def test_get_subject_for_page(briefing):
    d = load(briefing)
    assert get_subject_for_page(d, 10) == "quantitative_reasoning"
    assert get_subject_for_page(d, 20) == "quantitative_reasoning"
    assert get_subject_for_page(d, 21) == "science_reasoning"
    assert get_subject_for_page(d, 36) == "reading_comprehension"
    assert get_subject_for_page(d, 50) == "reading_comprehension"
    assert get_subject_for_page(d, 5) is None   # outside coverage
    assert get_subject_for_page(d, 99) is None


def test_is_relevant_page(briefing):
    d = load(briefing)
    assert is_relevant_page(d, 10) is True
    assert is_relevant_page(d, 50) is True
    assert is_relevant_page(d, 9) is False
    assert is_relevant_page(d, 51) is False


def test_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        load("/nonexistent/path/briefing.md")


def test_invalid_subject_raises(tmp_path):
    content = """# Test

## Basic Info
- **file:** x.pdf
- **relevant_pages:** 1–10

## Subject Coverage
- **pages 1–10:** invalid_subject
"""
    p = tmp_path / "bad.md"
    p.write_text(content)
    with pytest.raises(ValueError, match="Invalid subject"):
        load(str(p))


def test_skip_subject_is_valid(tmp_path):
    content = """# Test

## Basic Info
- **file:** x.pdf
- **relevant_pages:** 1–20

## Subject Coverage
- **pages 1–10:** quantitative_reasoning
- **pages 11–20:** skip
"""
    p = tmp_path / "skip.md"
    p.write_text(content)
    d = load(str(p))
    assert get_subject_for_page(d, 15) == "skip"
