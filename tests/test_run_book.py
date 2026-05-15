"""
run_book.py orchestrator tests.

Fast (no API, no Docling): all tests here use monkeypatch/tmp_path.
Run: pytest tests/test_run_book.py -v
"""
import json
import os
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

FIXTURES = Path(__file__).parent / "fixtures"

import pipeline.run_book as rb


# ── RB-01 ──────────────────────────────────────────────────────────────────────
def test_rb_01_require_briefing_returns_dict_when_present(tmp_path):
    """require_briefing returns parsed briefing dict when .md exists."""
    pdf = tmp_path / "mybook.pdf"
    pdf.write_bytes(b"%PDF-1.4")
    import shutil
    shutil.copy(str(FIXTURES / "sample_briefing.md"), str(tmp_path / "mybook.md"))
    result = rb.require_briefing("mybook", str(pdf))
    assert isinstance(result, dict)
    assert "column_format" in result


# ── RB-02 ──────────────────────────────────────────────────────────────────────
def test_rb_02_require_briefing_raises_when_missing(tmp_path):
    """require_briefing raises FileNotFoundError when .md briefing absent."""
    pdf = tmp_path / "mybook.pdf"
    pdf.write_bytes(b"%PDF-1.4")
    with pytest.raises(FileNotFoundError) as exc:
        rb.require_briefing("mybook", str(pdf))
    msg = str(exc.value)
    assert "mybook.md" in msg or "briefing" in msg.lower()
    assert "CLAUDE.md" in msg or "template" in msg.lower()


# ── RB-03 ──────────────────────────────────────────────────────────────────────
def test_rb_03_validate_book_id_accepts_valid():
    """validate_book_id accepts alphanumeric + underscore book IDs."""
    rb.validate_book_id("rs_aggarwal_2023")
    rb.validate_book_id("book1")
    rb.validate_book_id("EXCEL_gr7")


# ── RB-04 ──────────────────────────────────────────────────────────────────────
def test_rb_04_validate_book_id_rejects_special_chars():
    """validate_book_id rejects book IDs with spaces or special chars."""
    with pytest.raises(ValueError, match="alphanumeric"):
        rb.validate_book_id("my book! (2025)")
    with pytest.raises(ValueError):
        rb.validate_book_id("book-name")
    with pytest.raises(ValueError):
        rb.validate_book_id("book.name")


# ── RB-05 ──────────────────────────────────────────────────────────────────────
def test_rb_05_get_status_unprocessed_book(tmp_path):
    """get_status returns all phases as not_started for a fresh book."""
    status = rb.get_status("mybook", scratch_dir=str(tmp_path), output_dir=str(tmp_path))
    assert status["book_id"] == "mybook"
    assert status["phase1"] == "not_started"
    assert status["phase2"] == "not_started"
    assert status["phase3"] == "not_started"
    assert status["phase4"] == "not_started"


# ── RB-06 ──────────────────────────────────────────────────────────────────────
def test_rb_06_get_status_detects_completed_phases(tmp_path):
    """get_status detects which phases have produced output."""
    # Simulate phase1 done: scratch/<book>/pages/ exists with at least one .md
    pages_dir = tmp_path / "mybook" / "pages"
    pages_dir.mkdir(parents=True)
    (pages_dir / "page_1.md").write_text("content")

    # Simulate phase2 done: page_map.json exists
    (tmp_path / "mybook" / "page_map.json").write_text(json.dumps({"pages": []}))

    status = rb.get_status("mybook", scratch_dir=str(tmp_path), output_dir=str(tmp_path))
    assert status["phase1"] == "complete"
    assert status["phase2"] == "complete"
    assert status["phase3"] == "not_started"
    assert status["phase4"] == "not_started"


# ── RB-07 ──────────────────────────────────────────────────────────────────────
def test_rb_07_run_calls_phases_in_order(tmp_path, monkeypatch):
    """run() calls phase1 → phase2 → phase3 → phase4 in that order."""
    call_order = []

    def fake_p1(book_id, pdf_path, scratch_dir=None, briefing_path=None):
        call_order.append("phase1")

    def fake_p2(book_id, scratch_dir=None, briefing_path=None):
        call_order.append("phase2")

    def fake_p3(book_id, scratch_dir=None, output_dir=None, briefing_path=None):
        call_order.append("phase3")

    def fake_p4(book_id, output_dir=None, scratch_dir=None, briefing_path=None):
        call_order.append("phase4")

    monkeypatch.setattr(rb, "_run_phase1", fake_p1)
    monkeypatch.setattr(rb, "_run_phase2", fake_p2)
    monkeypatch.setattr(rb, "_run_phase3", fake_p3)
    monkeypatch.setattr(rb, "_run_phase4", fake_p4)

    # Set up a valid PDF + briefing
    pdf = tmp_path / "mybook.pdf"
    pdf.write_bytes(b"%PDF-1.4")
    import shutil
    shutil.copy(str(FIXTURES / "sample_briefing.md"), str(tmp_path / "mybook.md"))

    rb.run(
        book_id="mybook",
        pdf_path=str(pdf),
        scratch_dir=str(tmp_path / "scratch"),
        output_dir=str(tmp_path / "output"),
    )

    assert call_order == ["phase1", "phase2", "phase3", "phase4"]


# ── RB-08 ──────────────────────────────────────────────────────────────────────
def test_rb_08_run_raises_when_pdf_missing(tmp_path):
    """run() raises FileNotFoundError when PDF does not exist."""
    with pytest.raises(FileNotFoundError):
        rb.run(
            book_id="mybook",
            pdf_path=str(tmp_path / "nonexistent.pdf"),
            scratch_dir=str(tmp_path / "scratch"),
            output_dir=str(tmp_path / "output"),
        )


# ── RB-09 ──────────────────────────────────────────────────────────────────────
def test_rb_09_run_refuses_without_briefing(tmp_path):
    """run() raises FileNotFoundError when briefing file is missing."""
    pdf = tmp_path / "mybook.pdf"
    pdf.write_bytes(b"%PDF-1.4")
    # No .md briefing file created
    with pytest.raises(FileNotFoundError) as exc:
        rb.run(
            book_id="mybook",
            pdf_path=str(pdf),
            scratch_dir=str(tmp_path / "scratch"),
            output_dir=str(tmp_path / "output"),
        )
    assert "briefing" in str(exc.value).lower() or "mybook.md" in str(exc.value)
