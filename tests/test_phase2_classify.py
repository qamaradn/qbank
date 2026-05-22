"""Phase 2 — page map builder tests."""
import json
import pytest
from pathlib import Path
from pipeline.phase2_classify import run


@pytest.fixture
def briefing_file(tmp_path):
    content = """# Test

## Basic Info
- **file:** test.pdf
- **relevant_pages:** 45–50
- **target_year:** 9-10
- **difficulty:** medium

## Subject Coverage
- **pages 45–47:** quantitative_reasoning
- **pages 48–50:** science_reasoning
"""
    p = tmp_path / "test.md"
    p.write_text(content)
    return str(p)


def test_run_creates_page_map(briefing_file, tmp_path):
    scratch = str(tmp_path / "scratch")
    result = run(book_id="testbook", briefing_path=briefing_file, scratch_dir=scratch)
    page_map_path = Path(scratch) / "testbook" / "page_map.json"
    assert page_map_path.exists()
    assert result["book_id"] == "testbook"


def test_page_map_subjects(briefing_file, tmp_path):
    scratch = str(tmp_path / "scratch")
    result = run(book_id="testbook", briefing_path=briefing_file, scratch_dir=scratch)
    pages = {p["page_number"]: p["subject"] for p in result["pages"]}
    assert pages[45] == "quantitative_reasoning"
    assert pages[47] == "quantitative_reasoning"
    assert pages[48] == "science_reasoning"
    assert pages[50] == "science_reasoning"


def test_page_map_json_persisted(briefing_file, tmp_path):
    scratch = str(tmp_path / "scratch")
    run(book_id="testbook", briefing_path=briefing_file, scratch_dir=scratch)
    page_map_path = Path(scratch) / "testbook" / "page_map.json"
    data = json.loads(page_map_path.read_text())
    assert data["book_id"] == "testbook"
    assert len(data["pages"]) == 6  # pages 45–50
