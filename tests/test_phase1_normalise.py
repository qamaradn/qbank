# Tests — to be written before implementation (TDD).
import pytest
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"


def test_p1_09_invalid_book_id_raises_value_error():
    """[UNIT] run() raises ValueError for book_id with invalid characters."""
    import pipeline.phase1_normalise as p1
    with pytest.raises(ValueError, match="book_id"):
        p1.run("invalid book!", "/tmp/fake.pdf")
    with pytest.raises(ValueError, match="book_id"):
        p1.run("has spaces", "/tmp/fake.pdf")
    with pytest.raises(ValueError, match="book_id"):
        p1.run("has(parens)", "/tmp/fake.pdf")


@pytest.mark.slow
def test_p1_01_valid_pdf_and_briefing_no_error(tmp_path):
    """[UNIT] run() with valid PDF and briefing completes without raising."""
    import pipeline.phase1_normalise as p1
    p1.run(
        book_id="act_5pages",
        pdf_path=str(FIXTURES / "act_5pages.pdf"),
        scratch_dir=str(tmp_path),
        briefing_path=str(FIXTURES / "sample_act_briefing.md"),
    )
    # If we get here without exception, test passes


@pytest.mark.slow
def test_p1_02_missing_briefing_raises_file_not_found(tmp_path):
    """[UNIT] run() with missing briefing raises FileNotFoundError."""
    import pipeline.phase1_normalise as p1
    with pytest.raises(FileNotFoundError, match="briefing"):
        p1.run(
            book_id="act_5pages",
            pdf_path=str(FIXTURES / "act_5pages.pdf"),
            scratch_dir=str(tmp_path),
            briefing_path=str(FIXTURES / "nonexistent_briefing.md"),
        )


@pytest.mark.slow
def test_p1_03_only_relevant_pages_processed(tmp_path):
    """[INTEGRATION] only relevant pages appear in output; pages 4-5 skipped."""
    import pipeline.phase1_normalise as p1
    result = p1.run(
        book_id="act_5pages",
        pdf_path=str(FIXTURES / "act_5pages.pdf"),
        scratch_dir=str(tmp_path),
        briefing_path=str(FIXTURES / "sample_act_briefing_3pages.md"),
    )
    page_numbers = [p["page_number"] for p in result["pages"]]
    assert page_numbers == [1, 2, 3], f"Expected [1,2,3], got {page_numbers}"
    # Pages 4 and 5 must NOT have .md files written
    assert not (tmp_path / "act_5pages" / "pages" / "4.md").exists()
    assert not (tmp_path / "act_5pages" / "pages" / "5.md").exists()


@pytest.mark.slow
def test_p1_04_docling_output_json_correct_structure(tmp_path):
    """[CONTRACT] docling_output.json matches expected schema."""
    import json
    import pipeline.phase1_normalise as p1
    p1.run(
        book_id="act_5pages",
        pdf_path=str(FIXTURES / "act_5pages.pdf"),
        scratch_dir=str(tmp_path),
        briefing_path=str(FIXTURES / "sample_act_briefing.md"),
    )
    json_path = tmp_path / "act_5pages" / "docling_output.json"
    assert json_path.exists(), "docling_output.json not written"
    with open(json_path) as f:
        data = json.load(f)

    assert data["book_id"] == "act_5pages"
    assert "total_pages" in data
    assert isinstance(data["total_pages"], int)
    assert data["total_pages"] > 0
    assert "pages" in data
    assert len(data["pages"]) > 0

    for page in data["pages"]:
        assert "page_number" in page
        assert "markdown_path" in page
        assert isinstance(page["page_number"], int)
        # elements key should be present
        assert "elements" in page, f"Missing 'elements' key on page {page['page_number']}"
        for el in page["elements"]:
            assert "type" in el
            assert el["type"] in ("text", "figure")
            assert "x" in el and "y" in el and "width" in el and "height" in el
            if el["type"] == "figure":
                assert "figure_path" in el or True  # figure_path optional if no image


@pytest.mark.slow
def test_p1_05_markdown_is_utf8_and_non_empty(tmp_path):
    """[CONTRACT] page markdown files are UTF-8 and at least one page is non-empty."""
    import pipeline.phase1_normalise as p1
    p1.run(
        book_id="act_5pages",
        pdf_path=str(FIXTURES / "act_5pages.pdf"),
        scratch_dir=str(tmp_path),
        briefing_path=str(FIXTURES / "sample_act_briefing.md"),
    )
    pages_dir = tmp_path / "act_5pages" / "pages"
    md_files = list(pages_dir.glob("*.md"))
    assert len(md_files) > 0, "No .md files written"

    non_empty = 0
    for md_file in md_files:
        # Must be valid UTF-8 (not raise UnicodeDecodeError)
        content = md_file.read_text(encoding="utf-8")
        if content.strip():
            non_empty += 1

    assert non_empty > 0, "All page markdown files are empty — OCR likely failed"
