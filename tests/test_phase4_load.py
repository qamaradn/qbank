"""Phase 4 — dedup and load tests."""
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pytest
from pipeline.phase4_load import load_book, _is_duplicate


def _make_db(tmp_path):
    db_path = str(tmp_path / "test.db")
    schema = (Path(__file__).parent.parent / "db" / "schema.sql").read_text()
    conn = sqlite3.connect(db_path)
    conn.executescript(schema)
    conn.commit()
    conn.close()
    return db_path


def _make_question(stem="What is 2+2?", subject="quantitative_reasoning", **kwargs):
    q = {
        "id": str(uuid.uuid4()),
        "subject": subject,
        "stem": stem,
        "option_a": "3", "option_b": "4", "option_c": "5", "option_d": "6",
        "correct_answer": "B",
        "explanation": "Basic addition.",
        "topic": "Number",
        "difficulty": "medium",
        "confidence": 0.95,
        "source_book": "testbook",
        "source_page": 1,
        "source_page_description": "A maths page.",
        "passage": None,
        "review_status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    q.update(kwargs)
    return q


def _write_generated(output_dir, subject, book_id, page_n, questions):
    out = Path(output_dir) / subject / "generated"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{book_id}_p{page_n}.json").write_text(json.dumps(questions))


def test_is_duplicate_exact():
    stems = ["What is 2+2?", "Name the capital of Australia."]
    assert _is_duplicate("What is 2+2?", stems, 0.85) is True


def test_is_duplicate_different():
    stems = ["What is 2+2?"]
    assert _is_duplicate("Solve for x when 3x = 9.", stems, 0.85) is False


def test_is_duplicate_near_match():
    stems = ["What is 15% of 240?"]
    assert _is_duplicate("Name the largest river in Australia.", stems, 0.85) is False


def test_load_inserts_questions(tmp_path):
    db_path = _make_db(tmp_path)
    output_dir = str(tmp_path / "output")
    stems = [
        "A train travels 240 km in 3 hours. What is the speed?",
        "Name the capital city of Australia.",
        "What is the area of a rectangle with length 8m and width 5m?",
        "A bag has 3 red and 7 blue marbles. What is the probability of picking red?",
        "Solve for x: 2x + 6 = 14.",
    ]
    questions = [_make_question(stem) for stem in stems]
    _write_generated(output_dir, "quantitative_reasoning", "testbook", 1, questions)

    stats = load_book("testbook", output_dir=output_dir, db_path=db_path)
    assert stats["inserted"] == 5
    assert stats["duplicate"] == 0

    conn = sqlite3.connect(db_path)
    count = conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    conn.close()
    assert count == 5


def test_load_deduplicates(tmp_path):
    db_path = _make_db(tmp_path)
    output_dir = str(tmp_path / "output")

    # Pre-insert one question
    conn = sqlite3.connect(db_path)
    existing = _make_question("What is the square root of 144?")
    conn.execute(
        """INSERT INTO questions (id, subject, stem, option_a, option_b, option_c, option_d,
           correct_answer, explanation, topic, difficulty, confidence,
           source_book, source_page, source_page_description, review_status, created_at)
           VALUES (:id,:subject,:stem,:option_a,:option_b,:option_c,:option_d,
           :correct_answer,:explanation,:topic,:difficulty,:confidence,
           :source_book,:source_page,:source_page_description,:review_status,:created_at)""",
        existing,
    )
    conn.commit()
    conn.close()

    # Try to insert the same stem again
    questions = [_make_question("What is the square root of 144?")]
    _write_generated(output_dir, "quantitative_reasoning", "testbook", 2, questions)

    stats = load_book("testbook", output_dir=output_dir, db_path=db_path)
    assert stats["inserted"] == 0
    assert stats["duplicate"] == 1


def test_load_all_go_to_pending(tmp_path):
    db_path = _make_db(tmp_path)
    output_dir = str(tmp_path / "output")
    questions = [_make_question(f"Fresh question {i}?", confidence=0.99) for i in range(3)]
    _write_generated(output_dir, "quantitative_reasoning", "testbook", 1, questions)

    load_book("testbook", output_dir=output_dir, db_path=db_path)

    conn = sqlite3.connect(db_path)
    rows = conn.execute("SELECT review_status FROM questions").fetchall()
    conn.close()
    assert all(r[0] == "pending" for r in rows)


def test_load_no_files_returns_zero(tmp_path):
    db_path = _make_db(tmp_path)
    output_dir = str(tmp_path / "output")
    stats = load_book("nonexistent_book", output_dir=output_dir, db_path=db_path)
    assert stats["inserted"] == 0
