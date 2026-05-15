# Tests — to be written before implementation (TDD).
import pytest


def test_p1_09_invalid_book_id_raises_value_error():
    """[UNIT] run() raises ValueError for book_id with invalid characters."""
    import pipeline.phase1_normalise as p1
    with pytest.raises(ValueError, match="book_id"):
        p1.run("invalid book!", "/tmp/fake.pdf")
    with pytest.raises(ValueError, match="book_id"):
        p1.run("has spaces", "/tmp/fake.pdf")
    with pytest.raises(ValueError, match="book_id"):
        p1.run("has(parens)", "/tmp/fake.pdf")
