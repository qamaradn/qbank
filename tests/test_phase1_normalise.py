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
