"""
Phase 5 verification tests — P5-01 through P5-10.

All fast: mock Claude API, real SQLite.
Run: pytest tests/test_phase5_verify.py -v
"""
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

FIXTURES = Path(__file__).parent / "fixtures"

import pipeline.phase5_verify as p5


# ── DB helpers (same pattern as test_review_api.py) ──────────────────────────

def _init_db(path: str) -> sqlite3.Connection:
    schema = (Path(__file__).parent.parent / "db" / "schema.sql").read_text()
    conn = sqlite3.connect(path)
    conn.executescript(schema)
    conn.commit()
    return conn


def _make_question(**overrides) -> dict:
    """Build a minimal valid generated question dict."""
    defaults = {
        "id": str(uuid.uuid4()),
        "subject": "quantitative_reasoning",
        "stem": "What is 2 + 2?",
        "option_a": "3", "option_b": "4", "option_c": "5", "option_d": "6",
        "correct_answer": "B",
        "explanation": "2 + 2 = 4.",
        "writing_prompt": None,
        "year_level": "7-8",
        "difficulty": "medium",
        "topic": "arithmetic",
        "has_figure": False,
        "figure_path": None,
        "original_figure_path": None,
        "confidence": 0.95,
        "source_book": "test_book",
        "source_page": 1,
        "review_status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "reviewed_at": None,
        "edited": False,
    }
    defaults.update(overrides)
    return defaults


def _fake_claude_verify(answer: str, verified: bool = True):
    """Return a mock Claude client whose messages.create returns a verify response."""
    resp_text = json.dumps({
        "verified": verified,
        "answer": answer,
        "reasoning": "The calculation is correct.",
    })
    msg = MagicMock()
    msg.content = [MagicMock(text=resp_text)]
    client = MagicMock()
    client.messages.create.return_value = msg
    return client


# ── P5-01 ──────────────────────────────────────────────────────────────────────
def test_p5_01_high_confidence_auto_approved_without_api(tmp_path):
    """[TIER 1] confidence >= 0.90 → auto-approved, no Claude API call."""
    db_path = str(tmp_path / "test.db")
    _init_db(db_path)
    q = _make_question(confidence=0.95)

    fake_client = MagicMock()
    stats = p5.process_question(q, db_path, _claude_client=fake_client)

    fake_client.messages.create.assert_not_called()
    assert stats["tier"] == "auto_approved"

    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT review_status FROM questions WHERE id=?", (q["id"],)
    ).fetchone()
    conn.close()
    assert row[0] == "approved"


# ── P5-02 ──────────────────────────────────────────────────────────────────────
def test_p5_02_mid_confidence_claude_verifies_and_approves(tmp_path):
    """[TIER 2] 0.70 <= confidence < 0.90 → Claude verifies, approves on match."""
    db_path = str(tmp_path / "test.db")
    _init_db(db_path)
    q = _make_question(confidence=0.80, correct_answer="B")

    fake_client = _fake_claude_verify(answer="B", verified=True)
    stats = p5.process_question(q, db_path, _claude_client=fake_client)

    fake_client.messages.create.assert_called_once()
    assert stats["tier"] == "claude_approved"

    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT review_status FROM questions WHERE id=?", (q["id"],)
    ).fetchone()
    conn.close()
    assert row[0] == "approved"


# ── P5-03 ──────────────────────────────────────────────────────────────────────
def test_p5_03_low_confidence_stays_pending(tmp_path):
    """[TIER 3] confidence < 0.70 → inserted as pending, no Claude call."""
    db_path = str(tmp_path / "test.db")
    _init_db(db_path)
    q = _make_question(confidence=0.55)

    fake_client = MagicMock()
    stats = p5.process_question(q, db_path, _claude_client=fake_client)

    fake_client.messages.create.assert_not_called()
    assert stats["tier"] == "pending"

    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT review_status FROM questions WHERE id=?", (q["id"],)
    ).fetchone()
    conn.close()
    assert row[0] == "pending"


# ── P5-04 ──────────────────────────────────────────────────────────────────────
def test_p5_04_claude_disagrees_stays_pending(tmp_path):
    """[TIER 2] Claude picks different answer → stays pending for human review."""
    db_path = str(tmp_path / "test.db")
    _init_db(db_path)
    q = _make_question(confidence=0.80, correct_answer="B")

    # Claude says the answer is A (disagrees with B)
    fake_client = _fake_claude_verify(answer="A", verified=False)
    stats = p5.process_question(q, db_path, _claude_client=fake_client)

    assert stats["tier"] == "pending"

    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT review_status FROM questions WHERE id=?", (q["id"],)
    ).fetchone()
    conn.close()
    assert row[0] == "pending"


# ── P5-05 ──────────────────────────────────────────────────────────────────────
def test_p5_05_writing_question_skips_claude_verification(tmp_path):
    """[EDGE] Writing questions have no correct_answer — skip tier 2, use tier 1/3."""
    db_path = str(tmp_path / "test.db")
    _init_db(db_path)
    q = _make_question(
        subject="writing",
        confidence=0.80,
        correct_answer=None,
        option_a=None, option_b=None, option_c=None, option_d=None,
        writing_prompt="Write an essay about your favourite season.",
    )

    fake_client = MagicMock()
    stats = p5.process_question(q, db_path, _claude_client=fake_client)

    # No Claude call — writing questions can't be auto-verified
    fake_client.messages.create.assert_not_called()
    # confidence=0.80 would be tier 2 for MCQ but for writing → pending
    assert stats["tier"] == "pending"


# ── P5-06 ──────────────────────────────────────────────────────────────────────
def test_p5_06_figure_question_skips_claude_verification(tmp_path):
    """[EDGE] Figure questions skip Claude tier 2 (Claude can't see image)."""
    db_path = str(tmp_path / "test.db")
    _init_db(db_path)
    q = _make_question(
        confidence=0.80,
        has_figure=True,
        figure_path="/data/output/qr/figures/book_p1_e0_redrawn.png",
    )

    fake_client = MagicMock()
    stats = p5.process_question(q, db_path, _claude_client=fake_client)

    fake_client.messages.create.assert_not_called()
    assert stats["tier"] == "pending"


# ── P5-07 ──────────────────────────────────────────────────────────────────────
def test_p5_07_already_in_db_is_skipped(tmp_path):
    """[INTEGRATION] Question already in DB is skipped (resumable)."""
    db_path = str(tmp_path / "test.db")
    conn = _init_db(db_path)
    q = _make_question(confidence=0.95)

    # Pre-insert with approved status
    conn.execute(
        "INSERT INTO questions (id, subject, stem, option_a, option_b, option_c, option_d, "
        "correct_answer, explanation, writing_prompt, year_level, difficulty, topic, has_figure, "
        "figure_path, confidence, source_book, source_page, review_status, created_at, reviewed_at, edited) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (q["id"], q["subject"], q["stem"], q["option_a"], q["option_b"], q["option_c"], q["option_d"],
         q["correct_answer"], q["explanation"], None, q["year_level"], q["difficulty"], q["topic"],
         0, None, q["confidence"], q["source_book"], q["source_page"], "approved",
         q["created_at"], None, 0),
    )
    conn.commit()
    conn.close()

    fake_client = MagicMock()
    stats = p5.process_question(q, db_path, _claude_client=fake_client)

    assert stats["tier"] == "skipped"
    fake_client.messages.create.assert_not_called()


# ── P5-08 ──────────────────────────────────────────────────────────────────────
def test_p5_08_run_processes_all_generated_jsons(tmp_path, monkeypatch):
    """[INTEGRATION] run() scans generated/*.json for book and processes all questions."""
    db_path = str(tmp_path / "test.db")
    _init_db(db_path)

    output_dir = tmp_path / "output"
    gen_dir = output_dir / "quantitative_reasoning" / "generated"
    gen_dir.mkdir(parents=True)

    questions = [
        _make_question(confidence=0.95, source_book="test_book", stem="What is 2 plus 2?"),  # tier 1
        _make_question(confidence=0.55, source_book="test_book", stem="What is 3 plus 3?"),  # tier 3
    ]
    (gen_dir / "test_book_p1.json").write_text(
        json.dumps(questions), encoding="utf-8"
    )

    fake_client = MagicMock()
    monkeypatch.setattr(p5, "_get_claude_client", lambda: fake_client)

    stats = p5.run("test_book", output_dir=str(output_dir), db_path=db_path)

    assert stats["auto_approved"] == 1
    assert stats["pending"] == 1
    assert stats["claude_approved"] == 0
    assert stats["failed"] == 0

    conn = sqlite3.connect(db_path)
    rows = conn.execute("SELECT id, review_status FROM questions").fetchall()
    conn.close()
    assert len(rows) == 2


# ── P5-09 ──────────────────────────────────────────────────────────────────────
def test_p5_09_run_is_resumable(tmp_path, monkeypatch):
    """[INTEGRATION] run() skips questions already in DB."""
    db_path = str(tmp_path / "test.db")
    conn = _init_db(db_path)

    output_dir = tmp_path / "output"
    gen_dir = output_dir / "quantitative_reasoning" / "generated"
    gen_dir.mkdir(parents=True)

    q = _make_question(confidence=0.95, source_book="test_book")
    (gen_dir / "test_book_p1.json").write_text(json.dumps([q]), encoding="utf-8")

    # Pre-insert question
    conn.execute(
        "INSERT INTO questions (id, subject, stem, option_a, option_b, option_c, option_d, "
        "correct_answer, explanation, writing_prompt, year_level, difficulty, topic, has_figure, "
        "figure_path, confidence, source_book, source_page, review_status, created_at, reviewed_at, edited) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (q["id"], q["subject"], q["stem"], q["option_a"], q["option_b"], q["option_c"], q["option_d"],
         q["correct_answer"], q["explanation"], None, q["year_level"], q["difficulty"], q["topic"],
         0, None, q["confidence"], q["source_book"], q["source_page"], "approved",
         q["created_at"], None, 0),
    )
    conn.commit()
    conn.close()

    fake_client = MagicMock()
    monkeypatch.setattr(p5, "_get_claude_client", lambda: fake_client)

    stats = p5.run("test_book", output_dir=str(output_dir), db_path=db_path)

    assert stats["skipped"] == 1
    assert stats["auto_approved"] == 0
    fake_client.messages.create.assert_not_called()


# ── P5-10 ──────────────────────────────────────────────────────────────────────
def test_p5_10_verify_question_parses_claude_response(tmp_path):
    """[UNIT] verify_question() correctly parses Claude JSON response."""
    q = _make_question(confidence=0.80, correct_answer="C")
    fake_client = _fake_claude_verify(answer="C", verified=True)
    result = p5.verify_question(q, _claude_client=fake_client)
    assert result["verified"] is True
    assert result["claude_answer"] == "C"


# ── P5-11 ──────────────────────────────────────────────────────────────────────
def test_p5_11_near_duplicate_stem_skipped(tmp_path):
    """[DUPLICATE] near-duplicate stem in same subject is detected and skipped."""
    db_path = str(tmp_path / "test.db")
    conn = _init_db(db_path)

    original = _make_question(
        stem="What is the selling price of a bicycle bought for 640 dollars at 12 percent profit",
        subject="quantitative_reasoning",
        review_status="approved",
    )
    # Pre-insert the original
    conn.execute(
        "INSERT INTO questions (id, subject, stem, option_a, option_b, option_c, option_d, "
        "correct_answer, explanation, writing_prompt, year_level, difficulty, topic, has_figure, "
        "figure_path, confidence, source_book, source_page, review_status, created_at, reviewed_at, edited) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (original["id"], original["subject"], original["stem"],
         original["option_a"], original["option_b"], original["option_c"], original["option_d"],
         original["correct_answer"], original["explanation"], None,
         original["year_level"], original["difficulty"], original["topic"],
         0, None, original["confidence"], original["source_book"], original["source_page"],
         "approved", original["created_at"], None, 0),
    )
    conn.commit()
    conn.close()

    # Near-duplicate — same first 12 words after normalisation
    duplicate = _make_question(
        stem="What is the selling price of a bicycle bought for 640 dollars at 12 percent profit?",
        subject="quantitative_reasoning",
        confidence=0.95,
    )

    fake_client = MagicMock()
    stats = p5.process_question(duplicate, db_path, _claude_client=fake_client)

    assert stats["tier"] == "duplicate"
    fake_client.messages.create.assert_not_called()

    # Duplicate should NOT be in DB
    conn2 = sqlite3.connect(db_path)
    rows = conn2.execute("SELECT id FROM questions").fetchall()
    conn2.close()
    assert len(rows) == 1  # only original


# ── P5-12 ──────────────────────────────────────────────────────────────────────
def test_p5_12_is_near_duplicate_cross_subject_not_flagged(tmp_path):
    """[UNIT] same stem in different subject is NOT flagged as duplicate."""
    db_path = str(tmp_path / "test.db")
    conn = _init_db(db_path)
    original = _make_question(
        stem="What is the pattern in this sequence of numbers", subject="logical_reasoning"
    )
    conn.execute(
        "INSERT INTO questions (id, subject, stem, option_a, option_b, option_c, option_d, "
        "correct_answer, explanation, writing_prompt, year_level, difficulty, topic, has_figure, "
        "figure_path, confidence, source_book, source_page, review_status, created_at, reviewed_at, edited) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (original["id"], original["subject"], original["stem"],
         original["option_a"], original["option_b"], original["option_c"], original["option_d"],
         original["correct_answer"], original["explanation"], None,
         original["year_level"], original["difficulty"], original["topic"],
         0, None, original["confidence"], original["source_book"], original["source_page"],
         "approved", original["created_at"], None, 0),
    )
    conn.commit()

    # Same stem, different subject → not a duplicate
    different_subject = _make_question(
        stem="What is the pattern in this sequence of numbers", subject="science_reasoning"
    )
    result = p5.is_near_duplicate(conn, different_subject)
    conn.close()
    assert result is False


# ── P5-13 ──────────────────────────────────────────────────────────────────────
def test_p5_13_run_also_scans_figure_generated_jsons(tmp_path, monkeypatch):
    """[INTEGRATION] run() also picks up figures/*_generated.json (figure track)."""
    db_path = str(tmp_path / "test.db")
    _init_db(db_path)

    output_dir = tmp_path / "output"
    gen_dir = output_dir / "quantitative_reasoning" / "generated"
    fig_dir = output_dir / "quantitative_reasoning" / "figures"
    gen_dir.mkdir(parents=True)
    fig_dir.mkdir(parents=True)

    text_q = _make_question(confidence=0.95, source_book="test_book", stem="Text question alpha")
    fig_q = _make_question(
        confidence=0.90, source_book="test_book", stem="Figure question beta",
        has_figure=True, figure_path="/data/output/qr/figures/test_book_p1_e0_redrawn.png",
    )

    (gen_dir / "test_book_p1.json").write_text(json.dumps([text_q]), encoding="utf-8")
    (fig_dir / "test_book_p1_e0_generated.json").write_text(json.dumps([fig_q]), encoding="utf-8")

    fake_client = MagicMock()
    monkeypatch.setattr(p5, "_get_claude_client", lambda: fake_client)

    stats = p5.run("test_book", output_dir=str(output_dir), db_path=db_path)

    assert stats["auto_approved"] == 2   # both high-confidence → auto_approved
    assert stats["pending"] == 0
    assert stats["failed"] == 0

    conn = sqlite3.connect(db_path)
    rows = conn.execute("SELECT id FROM questions").fetchall()
    conn.close()
    assert len(rows) == 2  # both questions in DB
